from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from starlette.concurrency import run_in_threadpool
import asyncio
import logging
import os
import time

from .scraper import CytaScraper

log = logging.getLogger(__name__)


class Sim(BaseModel):
    msisdn: str
    balance_eur: float
    # Cyta shows pocket money as a second figure next to the balance.
    pocket_money_eur: Optional[float] = None


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

# A scrape drives one browser against one persistent profile directory. Two at
# once fight over it, so refreshes are serialised rather than allowed to stack.
_refresh_lock = asyncio.Lock()


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
    # Fill the cache in the background so the first caller is not the one
    # paying for it.
    asyncio.create_task(_periodic_refresh())


def _set_error(msg: str) -> None:
    global _cache, _last_refresh
    _cache = {"data": Balances(timestamp=int(time.time()), sims=[], error=msg)}
    _last_refresh = int(time.time())


async def _refresh_async() -> None:
    global _cache, _last_refresh, scraper
    if scraper is None:
        _set_error("Scraper is not initialized. Check credentials.")
        return
    async with _refresh_lock:
        try:
            sims = await run_in_threadpool(scraper.fetch_balances)
            # Converted field by field on purpose. The scraper returns stdlib
            # dataclasses, and pydantic v2 refuses those for a BaseModel field
            # without from_attributes — "Input should be a valid dictionary or
            # instance of Sim". The broad except below would have swallowed that
            # as just another scrape error, so the API would have kept reporting
            # failure with the scraping itself working.
            _cache = {
                "data": Balances(
                    timestamp=int(time.time()),
                    sims=[
                        Sim(
                            msisdn=s.msisdn,
                            balance_eur=s.balance_eur,
                            pocket_money_eur=getattr(s, "pocket_money_eur", None),
                        )
                        for s in sims
                    ],
                )
            }
            _last_refresh = int(time.time())
            log.info("refreshed %d SIMs", len(sims))
        except Exception as e:  # ловим всё
            log.warning("refresh failed: %s", e)
            _set_error(str(e))


async def _periodic_refresh() -> None:
    """Keep the cache warm on a timer.

    This exists because GET /api/balances used to do the scraping itself, inline.
    A scrape is a browser login plus one page per SIM — over a minute — while
    Home Assistant's REST sensor gives up after 30 seconds, so the very request
    that was supposed to deliver the balances always timed out and the sensor
    sat at `unavailable` forever. Now the endpoint only ever reads the cache.
    """
    while True:
        await _refresh_async()
        await asyncio.sleep(REFRESH_INTERVAL)


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True, "error": _cache["data"].error}


@app.get("/api/balances", response_model=Balances)
async def get_balances() -> Balances:
    # Returns immediately, always. If the cache is stale, a refresh is kicked
    # off in the background and the caller gets the previous figures — stale
    # numbers with a visible timestamp beat a timeout with none.
    if int(time.time()) - _last_refresh >= REFRESH_INTERVAL:
        asyncio.create_task(_refresh_async())
    return _cache["data"]


@app.post("/api/refresh", response_model=Balances)
async def force_refresh() -> Balances:
    # The one place that waits: an explicit manual trigger, from the dashboard
    # button or by hand. Never returns an HTTP error — the payload carries it.
    try:
        await _refresh_async()
    except Exception as e:
        _set_error(str(e))
    return _cache["data"]
