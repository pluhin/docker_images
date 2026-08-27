"""HTTP-обёртка над детектором.

Home Assistant вызывает /detect через rest_command с response_variable и читает
вердикт прямо в автоматизации. Поэтому эндпоинт принимает и отдаёт JSON, а не
файлы: путь к кадру приходит строкой, картинку сервис забирает сам.

Забирает он её с самого Home Assistant — entity_picture у image-сущностей уже
подписан, отдельная авторизация не нужна. Под работает в hostNetwork, так что
127.0.0.1:8123 — это и есть HA на той же машине.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

import requests
from fastapi import FastAPI
from pydantic import BaseModel

from .detector import ANIMAL_LABELS, get_detector

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

HA_BASE = os.getenv("HA_BASE", "http://127.0.0.1:8123")
FETCH_TIMEOUT = float(os.getenv("FETCH_TIMEOUT", "15"))
MAX_BYTES = int(os.getenv("MAX_BYTES", str(12 * 1024 * 1024)))

app = FastAPI(title="Cat Detector", version="1.0.0")


class DetectRequest(BaseModel):
    # Либо путь на HA («/api/image_proxy/...»), либо полный URL.
    path: Optional[str] = None
    url: Optional[str] = None


class Hit(BaseModel):
    label: str
    confidence: float
    box: List[int]


class DetectResponse(BaseModel):
    ok: bool
    has_cat: bool = False
    has_animal: bool = False
    has_person: bool = False
    best_label: str = "—"
    best_confidence: float = 0.0
    detections: List[Hit] = []
    elapsed_ms: int = 0
    error: Optional[str] = None


@app.get("/healthz")
async def healthz() -> dict:
    try:
        get_detector()
        return {"ok": True}
    except Exception as e:  # модель не загрузилась — под не должен считаться живым
        return {"ok": False, "error": str(e)}


def _fetch(req: DetectRequest) -> bytes:
    url = req.url or (HA_BASE + (req.path or ""))
    if not (req.url or req.path):
        raise ValueError("нужен path или url")
    r = requests.get(url, timeout=FETCH_TIMEOUT, stream=True)
    r.raise_for_status()
    data = r.raw.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"кадр больше {MAX_BYTES} байт")
    if not data:
        raise ValueError("пустой ответ")
    return data


@app.post("/detect", response_model=DetectResponse)
async def detect(req: DetectRequest) -> DetectResponse:
    # Ошибку возвращаем телом, а не HTTP-кодом: rest_command в HA на не-2xx
    # просто ругается в лог, и автоматизация теряет причину.
    try:
        data = _fetch(req)
    except Exception as e:
        log.warning("не удалось забрать кадр: %s", e)
        return DetectResponse(ok=False, error=f"fetch: {e}")

    try:
        hits, elapsed = get_detector().detect(data)
    except Exception as e:
        log.warning("детекция не удалась: %s", e)
        return DetectResponse(ok=False, error=f"detect: {e}")

    labels = {h.label for h in hits}
    best = hits[0] if hits else None
    log.info("кадр %d байт -> %s за %d мс",
             len(data), ", ".join(f"{h.label}:{h.confidence}" for h in hits) or "пусто",
             elapsed)
    return DetectResponse(
        ok=True,
        has_cat="cat" in labels,
        has_animal=bool(labels & ANIMAL_LABELS),
        has_person="person" in labels,
        best_label=best.label if best else "—",
        best_confidence=best.confidence if best else 0.0,
        detections=[Hit(label=h.label, confidence=h.confidence, box=h.box) for h in hits],
        elapsed_ms=elapsed,
    )
