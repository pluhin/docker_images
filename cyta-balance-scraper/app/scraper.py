from playwright.sync_api import sync_playwright
from dataclasses import dataclass
from typing import List
import re, os


LOGIN_URL = "https://www.cyta.com.cy/m-login/en"
HOME_URL = "https://www.cyta.com.cy/my-cyta/en"


class ScrapeError(Exception):
pass


@dataclass
class Sim:
msisdn: str
balance_eur: float


class CytaScraper:
def __init__(self, user: str, password: str, headless: bool = True, storage_state_path: str = "/data/storage_state.json"):
if not user or not password:
raise ScrapeError("CYTA_USER/CYTA_PASS are required")
self.user = user
self.password = password
self.headless = headless
self.storage_state_path = storage_state_path


def _login_and_save_state(self, page):
page.goto(LOGIN_URL, wait_until="domcontentloaded")
# формы часто имеют такие селекторы
page.fill("input[name='username'], #username", self.user)
page.fill("input[name='password'], #password", self.password)
page.get_by_role("button", name=re.compile("Log ?in|Σύνδεση", re.I)).click()
page.wait_for_load_state("networkidle")


def fetch_balances(self) -> List[Sim]:
with sync_playwright() as p:
browser = p.chromium.launch(headless=self.headless, args=["--no-sandbox"]) # k8s-friendly
context = p.chromium.launch_persistent_context(
user_data_dir=os.path.dirname(self.storage_state_path) or "/data",
headless=self.headless,
args=["--no-sandbox"],
)
page = context.new_page()
try:
page.goto(HOME_URL, wait_until="domcontentloaded")
if "my-cyta" not in page.url:
self._login_and_save_state(page)
page.goto(HOME_URL, wait_until="networkidle")
# из видимого текста забираем номера и суммы
text = page.evaluate("() => document.body.innerText")
phones = re.findall(r"(?:\+?357[- ]?)?(\d{8})", text)
amounts = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:€|EUR)", text)
sims: List[Sim] = []
# сопоставляем по порядку (практика показывает, что работает для карточек услуг)
for i, ph in enumerate(phones):
if i < len(amounts):
eur = float(amounts[i].replace(",", "."))
sims.append(Sim(msisdn=f"+357{ph}", balance_eur=eur))
if not sims:
raise ScrapeError("No SIM balances found on My Cyta page")
browser.close()