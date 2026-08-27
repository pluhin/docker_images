FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app MODEL_DIR=/model

# opencv-python-headless тянет libGL и friends только в полной сборке; headless
# обходится этим набором. curl нужен на этапе загрузки модели.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Модель кладётся в образ, а не скачивается в рантайме: под должен подниматься
# без интернета и без тома. YOLOv4-tiny — 23 МБ, COCO-классы, среди них cat.
# Если ссылки протухнут, сборка упадёт здесь и это будет видно, а не появится
# втихую образ без модели.
RUN mkdir -p /model && \
    curl -fsSL -o /model/coco.names \
      https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names && \
    curl -fsSL -o /model/yolov4-tiny.cfg \
      https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg && \
    curl -fsSL -o /model/yolov4-tiny.weights \
      https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights && \
    curl -fsSL -o /model/yolov4.cfg \
      https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg && \
    curl -fsSL -o /model/yolov4.weights \
      https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights && \
    test -s /model/yolov4.weights && test -s /model/yolov4-tiny.weights && \
    grep -qx cat /model/coco.names

COPY ./app /app/app

RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app /model
USER appuser

RUN python -m py_compile /app/app/main.py /app/app/detector.py

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
