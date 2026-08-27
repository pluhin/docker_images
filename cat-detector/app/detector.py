"""Распознавание объектов на одном кадре.

ЗАЧЕМ ЭТО ВООБЩЕ. У камер Eufy есть собственная детекция животных, но она
помечена Beta и ошибается в обе стороны — на этой установке она уверенно
опознала человека как животное. Строить на её вердикте счётчики котов нельзя.
Здесь берётся COCO-модель, где `cat` — штатный класс наравне с `person`.

ПОЧЕМУ КАДР, А НЕ ПОТОК. Камеры на солнечных батареях. Постоянный RTSP их
высадит, поэтому детекция работает по одному снимку на событие: камера и так
просыпается на своё PIR, дополнительного расхода нет.

ПОЧЕМУ OpenCV DNN, А НЕ TORCH. Ultralytics тянет torch и превращает образ в
несколько гигабайт. Здесь один YOLOv4-tiny на CPU: несколько десятков кадров в
сутки такой модели незаметны, а образ остаётся небольшим и разворачивается на домашней
ноде за секунды.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np

log = logging.getLogger(__name__)

MODEL_DIR = os.getenv("MODEL_DIR", "/model")
# Полная YOLOv4 по умолчанию, tiny остаётся вариантом на слабое железо.
# Замер на реальных кадрах с этих камер: tiny нашла человека на одном кадре из
# четырёх, хотя человек был на всех. Дело не в разрешении — кадры событий тут
# 440x328…600x448, а не миниатюры; дело в самой модели, ночью в инфракрасе она
# просто не видит. Полная тяжелее в разы, но десятки кадров в сутки этого
# не заметят.
MODEL_NAME = os.getenv("MODEL_NAME", "yolov4")
CFG = os.path.join(MODEL_DIR, f"{MODEL_NAME}.cfg")
WEIGHTS = os.path.join(MODEL_DIR, f"{MODEL_NAME}.weights")
NAMES = os.path.join(MODEL_DIR, "coco.names")

# Порог по умолчанию низкий намеренно. Кот ночью в инфракрасе — маленькое пятно
# низкого контраста, и на 0.5 модель его теряет. Ложное «кот» дешевле пропуска:
# кадр всё равно попадает в галерею и решает глаз.
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", "0.25"))
NMS_THRESHOLD = float(os.getenv("NMS_THRESHOLD", "0.4"))
# 608, а не 416: кадры приходят крупнее миниатюр, и на мелких объектах вроде
# кота в углу двора больший вход заметно поднимает попадания.
INPUT_SIZE = int(os.getenv("INPUT_SIZE", "608"))

# Что считаем «животным». Собака и медведь тут не опечатка: ночной кот в ИК
# регулярно опознаётся как dog, а изредка как bear — форма силуэта ближе, чем
# кажется. Для задачи «кто-то живой и не человек» это один класс.
ANIMAL_LABELS = {"cat", "dog", "bear", "horse", "sheep", "cow", "bird"}

# Доля кадра, выше которой «животное» не принимается всерьёз.
#
# Замер 27.08.2026: человек, прошедший вплотную к камере заднего двора, был
# опознан как cat 0.419 — силуэт крупным планом в инфракрасе действительно похож.
# Настоящий кот в этих кадрах мелкий: он на земле, в нескольких метрах, и
# половину кадра занять не может. Поэтому животное, занявшее больше трети
# кадра, — это почти наверняка человек вплотную, и считать его котом нельзя.
MAX_ANIMAL_AREA = float(os.getenv("MAX_ANIMAL_AREA", "0.35"))


@dataclass
class Detection:
    label: str
    confidence: float
    box: List[int]
    area: float = 0.0        # доля кадра, 0..1
    oversized: bool = False  # животное неправдоподобного размера


class Detector:
    def __init__(self) -> None:
        for path in (CFG, WEIGHTS, NAMES):
            if not os.path.exists(path):
                raise RuntimeError(f"нет файла модели: {path}")
        with open(NAMES, encoding="utf-8") as fh:
            self.classes = [line.strip() for line in fh if line.strip()]
        net = cv2.dnn.readNetFromDarknet(CFG, WEIGHTS)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(
            scale=1 / 255.0, size=(INPUT_SIZE, INPUT_SIZE), swapRB=True
        )
        log.info("модель загружена: %d классов, вход %dx%d",
                 len(self.classes), INPUT_SIZE, INPUT_SIZE)

    def detect(self, image_bytes: bytes) -> tuple[List[Detection], int]:
        started = time.monotonic()
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("не удалось декодировать изображение")

        # Кадры событий у Eufy — миниатюры около 288x162. Апскейл до входного
        # размера сети даёт заметно больше попаданий на мелких объектах, чем
        # паддинг: терять там уже нечего, разрешение и так на пределе.
        h, w = frame.shape[:2]
        if max(h, w) < INPUT_SIZE:
            scale = INPUT_SIZE / max(h, w)
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)),
                               interpolation=cv2.INTER_CUBIC)

        class_ids, scores, boxes = self.model.detect(
            frame, confThreshold=CONF_THRESHOLD, nmsThreshold=NMS_THRESHOLD
        )
        fh, fw = frame.shape[:2]
        frame_area = float(fh * fw) or 1.0
        out: List[Detection] = []
        for cid, score, box in zip(np.array(class_ids).flatten(),
                                   np.array(scores).flatten(),
                                   np.array(boxes).reshape(-1, 4) if len(boxes) else []):
            label = self.classes[int(cid)] if int(cid) < len(self.classes) else str(cid)
            b = [int(v) for v in box]
            area = round((b[2] * b[3]) / frame_area, 3)
            out.append(Detection(
                label=label, confidence=round(float(score), 3), box=b, area=area,
                oversized=(label in ANIMAL_LABELS and area > MAX_ANIMAL_AREA),
            ))
        out.sort(key=lambda d: d.confidence, reverse=True)
        return out, int((time.monotonic() - started) * 1000)


_detector: Optional[Detector] = None


def get_detector() -> Detector:
    global _detector
    if _detector is None:
        _detector = Detector()
    return _detector
