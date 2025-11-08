from playwright.sync_api import sync_playwright
from dataclasses import dataclass
from typing import List, Optional
import re
import os
import socket

BROWSER = os.getenv("BROWSER", "chromium").lower()  # chromium|webkit|firefox

LOGIN_URL = "https://www.cyta.com.cy/m-login/en"
HOME_URL = "https://www.cyta.com.cy/my-cyta/en"


class ScrapeError(Exception):
    pass


@dataclass
class Sim:
    msisdn: str
    balance_eur: float


class CytaScraper:
    def __init__(
        self,
        user: str,
        password: str,
        headless: bool = True,
        storage_state_path: str = "/data/storage_state.json",
    ):
        if not user or not password:
            raise ScrapeError("CYTA_USER/CYTA_PASS are required")
        self.user = user
        self.password = password
        self.headless = headless
        self.storage_state_path = storage_state_path
    def _accept_cookies(self, page) -> None:
        # Cookiebot
        try:
            dlg = page.locator("#CybotCookiebotDialog")
            if dlg.is_visible(timeout=2000):
                for txt in (r"Allow all", r"Allow selection", r"Accept", r"Συμφωνώ"):
                    btn = dlg.get_by_role("button", name=re.compile(txt, re.I))
                    if btn.count() > 0:
                        btn.first.click(timeout=3000)
                        page.wait_for_load_state("domcontentloaded", timeout=5000)
                        break
        except Exception:
            pass

    def _login(self, page) -> None:
        # Идём НАПРЯМУЮ на страницу логина
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        self._accept_cookies(page)

        # Заполняем логин/пароль (несколько вариантов селекторов)
        for sel in ["input[name='username']", "#username", "input[type='email']"]:
            try:
                page.fill(sel, self.user, timeout=3000); break
            except Exception:
                continue
        for sel in ["input[name='password']", "#password", "input[type='password']"]:
            try:
                page.fill(sel, self.password, timeout=3000); break
            except Exception:
                continue

        # Кнопка входа
        for pat in (r"Log ?in", r"Σύνδεση", r"Sign ?in"):
            try:
                page.get_by_role("button", name=re.compile(pat, re.I)).click(timeout=5000)
                break
            except Exception:
                continue

        # Ждём, что уйдём со страницы логина (редирект в ЛК)
        try:
            page.wait_for_url(re.compile(r"/my-?cyta/|/dashboard|/home", re.I), timeout=20000)
        except Exception:
            # Если не редиректнуло — открываем домашнюю ЛК вручную
            page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)

    def _ensure_logged_in(self, page) -> None:
        # Если уже в личном кабинете — выходим
        if re.search(r"/my-?cyta/", page.url, re.I):
            return

        self._accept_cookies(page)

        # На промо-странице “Login to My Cyta” чаще как BUTTON
        try:
            login_btn = page.get_by_role("button", name=re.compile(r"Login to\s*Μ?y\s*Cyta", re.I))
            if login_btn.count() > 0:
                login_btn.first.click(timeout=8000)
                page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

        # Если всё ещё не на форме логина — идём напрямую
        if not re.search(r"login|sign-?in|m-?login", page.url, re.I):
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)

        self._accept_cookies(page)

        # Поля логина — пробуем несколько селекторов
        for sel_user in ["input[name='username']", "#username", "input[type='email']"]:
            try:
                page.fill(sel_user, self.user, timeout=3000); break
            except Exception:
                continue
        for sel_pass in ["input[name='password']", "#password", "input[type='password']"]:
            try:
                page.fill(sel_pass, self.password, timeout=3000); break
            except Exception:
                continue

        # Кнопка входа
        for pat in (r"Log ?in", r"Σύνδεση", r"Sign ?in"):
            try:
                page.get_by_role("button", name=re.compile(pat, re.I)).click(timeout=8000)
                break
            except Exception:
                continue

        page.wait_for_load_state("domcontentloaded", timeout=20000)

    def _login_and_save_state(self, page) -> None:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        page.fill("input[name='username'], #username", self.user)
        page.fill("input[name='password'], #password", self.password)
        page.get_by_role("button", name=re.compile("Log ?in|Σύνδεση", re.I)).click()
        page.wait_for_load_state("domcontentloaded", timeout=30000)

    def _resolve_ipv4(self, host: str) -> Optional[str]:
        try:
            for fam, _, _, _, addr in socket.getaddrinfo(host, 443, family=socket.AF_INET):
                if fam == socket.AF_INET:
                    return addr[0]
        except Exception:
            return None
        return None

    def _norm_amount(self, s: str) -> float:
        # нормализуем 1 234,56 или 1.234,56 или 1234.56
        s = s.replace('\u00A0', ' ').strip()  # NBSP -> space
        m = re.search(r'(\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)', s)
        if not m:
            raise ScrapeError(f"Cannot parse amount from: {s!r}")
        num = m.group(1)
        # Если есть и точка и запятая – считаем, что запятая = десятичный, точки/пробелы = тысячи
        if ',' in num and '.' in num:
            num = num.replace('.', '').replace(',', '.')
        else:
            # только запятая -> десятичная
            if ',' in num and '.' not in num:
                num = num.replace(',', '.')
            # пробелы как разделители тысяч
            num = num.replace(' ', '')
        return float(num)

    def fetch_balances(self) -> List[Sim]:
        with sync_playwright() as p:
            browser = None
            context = None
            try:
                bt_map = {"chromium": p.chromium, "webkit": p.webkit, "firefox": p.firefox}
                browser_type = bt_map.get(BROWSER, p.chromium)

                proxy_server = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
                ctx_kwargs = dict(
                    user_data_dir=os.path.dirname(self.storage_state_path) or "/data",
                    headless=self.headless,
                    ignore_https_errors=True,
                )
                launch_args = []
                if BROWSER == "chromium":
                    ipv4 = self._resolve_ipv4("www.cyta.com.cy")
                    if ipv4:
                        launch_args.append(f"--host-resolver-rules=MAP www.cyta.com.cy {ipv4}")
                    extra = os.getenv("PLAYWRIGHT_CHROMIUM_ARGS", "")
                    if extra.strip():
                        launch_args += [x for x in extra.split() if x]
                    ctx_kwargs["args"] = launch_args

                if proxy_server:
                    ctx_kwargs["proxy"] = {"server": proxy_server}

                browser = browser_type.launch(headless=self.headless, args=launch_args if BROWSER == "chromium" else None)
                context = browser_type.launch_persistent_context(**ctx_kwargs)
                page = context.new_page()
                page.set_default_navigation_timeout(30000)

                # 1) Явный логин
                self._login(page)

                # 2) На всякий случай открываем домашнюю ЛК
                page.goto(HOME_URL, wait_until="domcontentloaded", timeout=30000)
                self._accept_cookies(page)

                # 3) Часто баланс в разделе Mobile — кликаем карточку/ссылку при наличии
                try:
                    mobile = page.get_by_role("link", name=re.compile(r"(mobile service|soeasy|prepaid|usage|balance)", re.I))
                    if mobile.count() == 0:
                        mobile = page.get_by_text(re.compile(r"Mobile service", re.I))
                    if mobile.count() > 0:
                        mobile.first.click(timeout=8000)
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                except Exception:
                    pass

                # Далее — твой парсинг текста/регэкспы (как уже сделано)
                text = page.evaluate("() => document.body ? document.body.innerText : ''")


                # 5) Ищем телефоны и суммы (надёжные регэкспы)
                phones = re.findall(r'(?<!\d)(?:\+?357[\s-]?)?(\d{8})(?!\d)', text)
                amounts_raw = re.findall(r'((?:\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)\s*(?:€|EUR))', text, flags=re.I)

                # 6) Нормализуем суммы
                amounts = []
                for a in amounts_raw:
                    try:
                        amounts.append(self._norm_amount(a))
                    except Exception:
                        continue

                sims: List[Sim] = []

                # 7) Если телефонов и сумм одинаково — спариваем по порядку
                if phones and amounts:
                    n = min(len(phones), len(amounts))
                    for i in range(n):
                        sims.append(Sim(msisdn=f"+357{phones[i]}", balance_eur=amounts[i]))

                # 8) Если не нашли — пробуем альтернативный DOM-поиск всех текстов с €
                if not sims:
                    try:
                        euro_texts = page.evaluate("""
                            () => Array.from(document.querySelectorAll('body *'))
                            .map(e => e.innerText)
                            .filter(t => t && /€|EUR/i.test(t))
                            .slice(0, 500)
                        """)
                        # ещё раз вытащим суммы
                        alt_amounts = []
                        for t in euro_texts:
                            m = re.findall(r'(?:\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)', t)
                            for x in m:
                                try:
                                    alt_amounts.append(self._norm_amount(x))
                                except Exception:
                                    pass
                        # телефоны из всего текста уже есть
                        if phones and alt_amounts:
                            n = min(len(phones), len(alt_amounts))
                            for i in range(n):
                                sims.append(Sim(msisdn=f"+357{phones[i]}", balance_eur=alt_amounts[i]))
                    except Exception:
                        pass

                # 9) Если всё ещё пусто — снимки для отладки, чтобы мы увидели реальную разметку
                if not sims:
                    try:
                        os.makedirs("/data", exist_ok=True)
                        with open("/data/last_mycyta.html", "w", encoding="utf-8") as f:
                            f.write(page.content())
                        with open("/data/last_mycyta.txt", "w", encoding="utf-8") as f:
                            f.write(text)
                        page.screenshot(path="/data/last_mycyta.png", full_page=True)
                    except Exception:
                        pass
                    raise ScrapeError("No SIM balances found on My Cyta page")

                return sims

            except Exception as e:
                raise ScrapeError(str(e))
            finally:
                try:
                    if context is not None:
                        context.close()
                finally:
                    if browser is not None:
                        browser.close()
