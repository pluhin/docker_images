from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from starlette.concurrency import run_in_threadpool
import os
import time

from .scraper import CytaScraper, ScrapeError


class Sim(BaseModel):
    msisdn: str
    balance_eur: float


class Balances(BaseModel):
    timestamp: int
    sims: List[Sim]
    error: Optional[str] = None


app = FastAPI(title="Cyta Balance API", version="1.0.0")

CYTA_USER = os.getenv("CYTA_USER")
CYTA_PASS = os.getenv("CYTA_PASS")
HEADLESS = os.getenv("HEADLESS", "1") == "1"
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "1800"))
STORAGE_PATH = os.getenv("STORAGE_PATH", "/data/storage_state.json")

scraper: Optional[CytaScraper] = None
_cache = {"data": Balances(timestamp=0, sims=[], error="not yet fetched")}
_last_refresh = 0


@app.on_event("startup")
async def _startup() -> None:
    global scraper
    if not CYTA_USER or not CYTA_PASS:
        _set_error("CYTA_USER/CYTA_PASS are not set in environment")
        return
    scraper = CytaScraper(
        user=CYTA_USER,
        password=CYTA_PASS,
        headless=HEADLESS,
        storage_state_path=STORAGE_PATH,
    )


def _set_error(msg: str) -> None:
    global _cache, _last_refresh
    _cache = {"data": Balances(timestamp=int(time.time()), sims=[], error=msg)}
    _last_refresh = int(time.time())


async def _refresh_async() -> None:
    global _cache, _last_refresh, scraper
    if scraper is None:
        _set_error("Scraper is not initialized. Check credentials.")
        return
    try:
        from starlette.concurrency import run_in_threadpool
        sims = await run_in_threadpool(scraper.fetch_balances)
        _cache = {"data": Balances(timestamp=int(time.time()), sims=sims)}
    except Exception as e:  # ловим всё
        _set_error(str(e))


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True, "error": _cache["data"].error}


@app.get("/api/balances", response_model=Balances)
async def get_balances() -> Balances:
    now = int(time.time())
    if now - _last_refresh >= REFRESH_INTERVAL:
        await _refresh_async()
    return _cache["data"]


@app.post("/api/refresh", response_model=Balances)
async def force_refresh() -> Balances:
    try:
        await _refresh_async()
    except Exception as e:
        # на всякий случай, но _refresh_async уже ловит всё
        _set_error(str(e))
    # НИЧЕГО не бросаем, всегда 200
    return _cache["data"]
