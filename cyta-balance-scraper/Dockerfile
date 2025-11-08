FROM python:3.12-slim


ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
HEADLESS=1 REFRESH_INTERVAL=1800 STORAGE_PATH=/data/storage_state.json


# Playwright deps
RUN apt-get update && apt-get install -y --no-install-recommends \
libnss3 libnspr4 libx11-6 libxkbfile1 libxcomposite1 libxcursor1 libxdamage1 \
libxi6 libxtst6 libayatana-appindicator3-1 libdrm2 libgbm1 libxrandr2 libasound2 \
fonts-liberation libxshmfence1 ca-certificates curl && \
rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY ./requirements.txt ./app/requirements.txt
RUN pip install -r ./app/requirements.txt && \
python -m playwright install --with-deps chromium


COPY ./app /app


# Non-root
RUN useradd -ms /bin/bash appuser && mkdir -p /data && chown -R appuser:appuser /data /app
USER appuser
VOLUME ["/data"]


EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]