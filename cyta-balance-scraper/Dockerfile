# База поднята с 3.12-slim 16.09.2026: на прежней Trivy нашёл критическую
# уязвимость с готовым исправлением, и обновление питоновских зависимостей
# её не закрыло — значит она в системных пакетах образа, а не в наших.
FROM python:3.13-slim

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Балансы SIM-карт Cyta по HTTP"
LABEL org.opencontainers.image.licenses=MIT

# Which Playwright browser to ship. The app defaults to webkit; building both
# webkit and chromium "на всякий случай" doubled the image for an engine that
# never gets launched. Override with --build-arg BROWSER=chromium if needed.
ARG BROWSER=webkit

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HEADLESS=1 REFRESH_INTERVAL=1800 STORAGE_PATH=/data/storage_state.json \
    PYTHONPATH=/app BROWSER=${BROWSER}

# Базовые зависимости + CA (root)
# apt-get upgrade здесь не для красоты. Базовый образ пересобирается реже,
# чем Debian выпускает security-обновления, и разница видна: 16.09.2026 Trivy
# остановил публикацию на трёх критических в perl-base (CVE-2026-13221,
# CVE-2026-42496, CVE-2026-8376), где исправление 5.40.1-6+deb13u1 уже лежало
# в security-репозитории, а в образе стояла 5.40.1-6.
#
# Обновляются все пакеты, а не один perl-base: набор дыр в базе меняется от
# месяца к месяцу, и перечислять их поимённо значит возвращаться сюда после
# каждой находки. Слой стоит несколько мегабайт.
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python-зависимости
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Системные deps для браузера — только root это может
RUN python -m playwright install-deps "$BROWSER" && \
    rm -rf /var/lib/apt/lists/*

# Код приложения. app/__init__.py теперь лежит в репозитории — раньше он
# создавался прямо в сборке, из-за чего пакет существовал только внутри образа
# и `python -m app.main` локально не работал.
COPY ./app /app/app

# Пользователь рантайма
RUN useradd -ms /bin/bash appuser && mkdir -p /data && chown -R appuser:appuser /app /data
USER appuser

# Браузер ставим уже под appuser: кеш ложится в ~/.cache/ms-playwright,
# и путь совпадает с тем, который ищет рантайм.
RUN python -m playwright install "$BROWSER"

# sanity-check питоновского синтаксиса
RUN python -m py_compile /app/app/main.py /app/app/scraper.py

EXPOSE 8080
VOLUME ["/data"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
