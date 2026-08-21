"""Scrape SIM balances out of the Cyta self-service portal.

Cyta moved authentication to Microsoft Identity and put the account area behind
an /az/ prefix. The old flow went to https://www.cyta.com.cy/my-cyta/en, which
now redirects to the public homepage — login still succeeded, so the saved page
carried a Logout link and the account initials, but the words "balance" and
"msisdn" appeared zero times on it. Hence the old, accurate but unhelpful,
"No SIM balances found on My Cyta page".

Rather than hard-code one replacement URL and break again at the next redesign,
this walks a list of candidate account pages and stops at the first one that
actually yields balances. Every attempt writes its HTML, text and a screenshot
to DEBUG_DIR, which is what made the original diagnosis possible at all.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from playwright.sync_api import sync_playwright

log = logging.getLogger(__name__)

BROWSER = os.getenv("BROWSER", "webkit").lower()  # webkit|chromium|firefox
DEBUG_DIR = os.getenv("DEBUG_DIR", "/data")

LOGIN_URL = "https://www.cyta.com.cy/m-login/en"

# Tried in order; the first page that yields balances wins. Override with
# CYTA_ACCOUNT_URLS (comma separated) when Cyta reshuffles things again.
DEFAULT_ACCOUNT_URLS = (
    "https://www.cyta.com.cy/az/mycyta-account",
    "https://www.cyta.com.cy/az/mycyta-details",
    "https://www.cyta.com.cy/az/mycyta",
    "https://www.cyta.com.cy/my-cyta/en",
)

# Cyprus mobile numbers are 8 digits starting with 9 (or 96/99...), optionally
# +357 prefixed. Anchored so it will not swallow parts of longer numbers.
PHONE_RE = re.compile(r"(?<!\d)(?:\+?357[\s\-]?)?(9\d{7})(?!\d)")
AMOUNT_RE = re.compile(
    r"(?:€|EUR)\s*(-?\d[\d.,\s]*)|(-?\d[\d.,\s]*)\s*(?:€|EUR)", re.I
)


class ScrapeError(Exception):
    pass


@dataclass
class Sim:
    msisdn: str
    balance_eur: float
    pocket_money_eur: Optional[float] = None


def _norm_amount(raw: str) -> float:
    """Turn '1 234,56' / '1.234,56' / '1234.56' into a float."""
    s = raw.replace(" ", " ").strip()
    m = re.search(
        r"(-?\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{1,2})?|-?\d+(?:[.,]\d{1,2})?)", s
    )
    if not m:
        raise ScrapeError(f"Cannot parse amount from {raw!r}")
    num = m.group(1)
    if "," in num and "." in num:
        # Both present: the last separator is the decimal one.
        num = num.replace(".", "").replace(",", ".") if num.rfind(",") > num.rfind(".") \
            else num.replace(",", "")
    elif "," in num:
        num = num.replace(",", ".")
    return float(num.replace(" ", ""))


class CytaScraper:
    def __init__(
        self,
        user: str,
        password: str,
        headless: bool = True,
        storage_state_path: str = "/data/storage_state.json",
    ) -> None:
        if not user or not password:
            raise ScrapeError("CYTA_USER/CYTA_PASS are required")
        self.user = user
        self.password = password
        self.headless = headless
        self.storage_state_path = storage_state_path

    # ---------------------------------------------------------------- helpers

    @property
    def account_urls(self) -> List[str]:
        env = os.getenv("CYTA_ACCOUNT_URLS", "").strip()
        if env:
            return [u.strip() for u in env.split(",") if u.strip()]
        return list(DEFAULT_ACCOUNT_URLS)

    def _accept_cookies(self, page) -> None:
        """Dismiss the consent banner. It overlays the page and swallows clicks.

        Two flavours seen on cyta.com.cy: the Cookiebot dialog and a plain
        button somewhere in the body.
        """
        for selector in ("#CybotCookiebotDialog", "[id*='ookie']", "[class*='ookie']"):
            try:
                box = page.locator(selector).first
                if not box.count() or not box.is_visible():
                    continue
                for name in ("Allow all", "Accept all", "Accept", "Allow selection",
                             "Συμφωνώ", "Αποδοχή"):
                    btn = box.get_by_role("button", name=re.compile(name, re.I))
                    if btn.count():
                        btn.first.click(timeout=3000)
                        page.wait_for_load_state("domcontentloaded", timeout=5000)
                        log.info("cookie banner dismissed via %s / %s", selector, name)
                        return
            except Exception:
                continue
        # Last resort: any top-level "Allow all" button.
        try:
            btn = page.get_by_role("button", name=re.compile(r"allow all|accept all", re.I))
            if btn.count():
                btn.first.click(timeout=3000)
                log.info("cookie banner dismissed via page-level button")
        except Exception:
            pass

    def _login(self, page) -> None:
        """Sign in through Azure AD B2C.

        /m-login/en no longer hosts a form — it redirects to
        login.cyta.com.cy/cytab2c.onmicrosoft.com/..., a standard B2C page whose
        fields are id=email (name="Email"), id=password (name="Password") and a
        submit button id=next. The previous code looked for name='username',
        which has never existed there, so the form was submitted empty at best.
        """
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
        # Dismiss consent first: the banner overlays the form and eats clicks.
        self._accept_cookies(page)
        log.info("login page: %s", page.url)

        filled_user = filled_pass = False
        for sel in ("#email", "input[name='Email']", "input[type='email']",
                    "#signInName", "input[name='signInName']"):
            try:
                page.fill(sel, self.user, timeout=3000)
                filled_user = True
                log.info("filled user via %s", sel)
                break
            except Exception:
                continue
        for sel in ("#password", "input[name='Password']", "input[type='password']"):
            try:
                page.fill(sel, self.password, timeout=3000)
                filled_pass = True
                log.info("filled password via %s", sel)
                break
            except Exception:
                continue
        if not (filled_user and filled_pass):
            self._dump(page, "login_form_not_found",
                       page.evaluate("() => document.body?.innerText || ''") or "")
            raise ScrapeError(
                f"login form not found at {page.url} "
                f"(user={filled_user}, pass={filled_pass})"
            )

        # #next is the B2C submit button. Prefer it over a by-role lookup: the
        # header also carries a "Login" link, which matched first before.
        clicked = False
        for sel in ("#next", "button[type='submit'][form='localAccountForm']",
                    "button[type='submit']"):
            try:
                page.click(sel, timeout=5000)
                clicked = True
                log.info("submitted via %s", sel)
                break
            except Exception:
                continue
        if not clicked:
            page.keyboard.press("Enter")

        # B2C posts back to www.cyta.com.cy, so wait to leave the identity host
        # rather than for one specific URL. It lands on a relay first —
        # /signin-oidc or /mp/account/loginidm.aspx — which carries no session
        # chrome at all, so waiting only for the host would test the wrong page.
        try:
            page.wait_for_url(re.compile(r"^https://www\.cyta\.com\.cy/"), timeout=30000)
        except Exception:
            log.warning("did not return to cyta.com.cy, still at %s", page.url)
        try:
            page.wait_for_url(
                lambda url: "signin-oidc" not in url and "loginidm" not in url,
                timeout=20000,
            )
        except Exception:
            log.info("still on the OIDC relay at %s, continuing anyway", page.url)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        log.info("after login: url=%s", page.url)

    def _is_logged_in(self, page) -> bool:
        """A Logout / signout link is the reliable marker; the URL is not."""
        try:
            html = page.content()
        except Exception:
            return False
        return bool(re.search(r"logout|signout|sign-out", html, re.I))

    def _dump(self, page, tag: str, text: str) -> None:
        try:
            os.makedirs(DEBUG_DIR, exist_ok=True)
            base = os.path.join(DEBUG_DIR, f"last_{tag}")
            with open(base + ".html", "w", encoding="utf-8") as fh:
                fh.write(page.content())
            with open(base + ".txt", "w", encoding="utf-8") as fh:
                fh.write(f"URL: {page.url}\n\n{text}")
            page.screenshot(path=base + ".png", full_page=True)
        except Exception:
            log.warning("could not write debug artifacts for %s", tag, exc_info=True)

    # ----------------------------------------------------------- the parsing

    # Each SIM is a selectable item on /az/mycyta, linked as
    # ?pId=<msisdn>&hId=<guid>&pType=GS&command=Selected. Selecting one renders
    # its balance under the label "Your balance is:". pId is the number itself,
    # so the SIM list needs no configuration — and the account also lists
    # non-mobile services, which the 9xxxxxxx shape filters out.
    BALANCE_RE = re.compile(
        r"Your balance is:?\s*(?:€|EUR)?\s*(-?[\d.,\s]+)", re.I
    )
    POCKET_RE = re.compile(r"Pocket money:?\s*(?:€|EUR)?\s*(-?[\d.,\s]+)", re.I)

    def _discover_sims(self, page) -> List[str]:
        hrefs = page.evaluate(
            """() => Array.from(document.querySelectorAll('a[href*="pId="]'))
                     .map(a => a.getAttribute('href'))"""
        ) or []
        out, seen = [], set()
        for href in hrefs:
            m = re.search(r"pId=(\d+)", href or "")
            if not m:
                continue
            pid = m.group(1)
            if not re.fullmatch(r"9\d{7}", pid) or pid in seen:
                continue
            seen.add(pid)
            out.append(href)
        log.info("discovered %d mobile services: %s", len(out), sorted(seen))
        return out

    def _scrape_sim(self, page, base: str, href: str) -> Optional[Sim]:
        pid = re.search(r"pId=(\d+)", href).group(1)
        url = href if href.startswith("http") else base.split("?")[0] + href
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # The balance block is rendered client-side after load.
        try:
            page.wait_for_function(
                "() => /Your balance is/i.test(document.body.innerText)", timeout=15000
            )
        except Exception:
            log.warning("balance label never appeared for %s", pid)

        text = page.evaluate("() => document.body ? document.body.innerText : ''") or ""
        m = self.BALANCE_RE.search(text)
        if not m:
            self._dump(page, f"sim_{pid}", text)
            log.warning("no balance for %s at %s", pid, page.url)
            return None
        try:
            balance = _norm_amount(m.group(1))
        except ScrapeError:
            log.warning("unparseable balance %r for %s", m.group(1), pid)
            return None

        pocket = None
        pm = self.POCKET_RE.search(text)
        if pm:
            try:
                pocket = _norm_amount(pm.group(1))
            except ScrapeError:
                pass
        log.info("SIM +357%s balance=%.2f pocket=%s", pid, balance, pocket)
        return Sim(msisdn=f"+357{pid}", balance_eur=balance, pocket_money_eur=pocket)

    # ------------------------------------------------------------- entrypoint

    def fetch_balances(self) -> List[Sim]:
        with sync_playwright() as p:
            browser_type = {"chromium": p.chromium, "webkit": p.webkit,
                            "firefox": p.firefox}.get(BROWSER, p.webkit)

            ctx_kwargs = dict(
                user_data_dir=os.path.dirname(self.storage_state_path) or "/data",
                headless=self.headless,
                ignore_https_errors=True,
            )
            proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
            if proxy:
                ctx_kwargs["proxy"] = {"server": proxy}

            # A persistent context IS the browser — the old code also called
            # browser_type.launch(), starting a second browser it never used.
            context = browser_type.launch_persistent_context(**ctx_kwargs)
            try:
                page = context.new_page()
                page.set_default_navigation_timeout(30000)

                self._login(page)

                # Login is verified on the first real account page, not at the
                # landing URL: B2C drops us on a relay that has no session
                # chrome, so checking there reported a failed login every time.
                verified = False
                for url in self.account_urls:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    self._accept_cookies(page)
                    if not verified:
                        if self._is_logged_in(page):
                            verified = True
                        else:
                            self._dump(page, "login_failed",
                                       page.evaluate("() => document.body?.innerText || ''") or "")
                            raise ScrapeError(
                                f"login appears to have failed, no logout link at {page.url}"
                            )
                    base = page.url
                    hrefs = self._discover_sims(page)
                    if not hrefs:
                        continue
                    sims = [s for s in (self._scrape_sim(page, base, h) for h in hrefs)
                            if s is not None]
                    if sims:
                        return sims

                text = page.evaluate("() => document.body?.innerText || ''") or ""
                self._dump(page, "no_sims", text)
                raise ScrapeError(
                    "logged in, but found no mobile services on "
                    + ", ".join(self.account_urls)
                    + f". Debug artifacts in {DEBUG_DIR}."
                )
            finally:
                try:
                    context.close()
                except Exception:
                    pass
