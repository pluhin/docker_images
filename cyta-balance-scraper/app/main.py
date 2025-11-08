from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os, time
from .scraper import CytaScraper, ScrapeError


class Sim(BaseModel):
msisdn: str
balance_eur: float


class Balances(BaseModel):
timestamp: int
sims: List[Sim]
error: Optional[str] = None


app = FastAPI(title="Cyta Balance API", version="1.0.0")


# Env
CYTA_USER = os.getenv("CYTA_USER")
CYTA_PASS = os.getenv("CYTA_PASS")
HEADLESS = os.getenv("HEADLESS", "1") == "1"
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "1800")) # seconds
STORAGE_PATH = os.getenv("STORAGE_PATH", "/data/storage_state.json")


scraper = CytaScraper(
user=CYTA_USER,
password=CYTA_PASS,
headless=HEADLESS,
storage_state_path=STORAGE_PATH,
)


_cache = {"data": Balances(timestamp=0, sims=[], error="not yet fetched")}
_last_refresh = 0


@app.on_event("startup")
def _startup():
_refresh()




def _refresh():
global _cache, _last_refresh
try:
sims = scraper.fetch_balances()
_cache = {"data": Balances(timestamp=int(time.time()), sims=sims)}
except ScrapeError as e:
_cache = {"data": Balances(timestamp=int(time.time()), sims=[], error=str(e))}
_last_refresh = int(time.time())




@app.get("/api/balances", response_model=Balances)
async def get_balances():
now = int(time.time())
if now - _last_refresh >= REFRESH_INTERVAL:
_refresh()
return _cache["data"]




@app.post("/api/refresh", response_model=Balances)
async def force_refresh():
_refresh()
if _cache["data"].error:
raise HTTPException(status_code=502, detail=_cache["data"].error)
return _cache["data"]