FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HEADLESS=1 REFRESH_INTERVAL=1800 STORAGE_PATH=/data/storage_state.json \
    PYTHONPATH=/app

# Базовые зависимости + CA (root)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python-зависимости
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# >>> ВАЖНО: системные deps для браузеров (ставим как root)
# Ставим под WebKit и Chromium на всякий случай
RUN python -m playwright install-deps webkit && \
    python -m playwright install-deps chromium

# Код приложения
COPY ./app /app/app
RUN python - <<'PY'
import os; open('/app/app/__init__.py','a').close(); print('init ok')
PY

# Пользователь рантайма
RUN useradd -ms /bin/bash appuser && mkdir -p /data && chown -R appuser:appuser /app /data
USER appuser

# >>> Браузеры ставим уже под appuser (путь кеша совпадёт с рантаймом)
# Если будешь использовать только WebKit — можно убрать chromium
RUN python -m playwright install webkit && \
    python -m playwright install chromium

# sanity-check питоновского синтаксиса
RUN python -m py_compile /app/app/main.py /app/app/scraper.py

EXPOSE 8080
VOLUME ["/data"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
