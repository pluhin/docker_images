# Снять дамп PostgreSQL и положить его в GCS.
FROM postgres:17-alpine

# Версия postgres закреплена на 17 намеренно: pg_dump должен быть не старше
# сервера, а сервер здесь семнадцатый. Поднимать её следом за сервером, а не
# впереди него.

# TARGETARCH подставляет buildx. Было жёстко x86_64 в имени архива, из-за чего
# сборка под arm64 давала образ с бинарником, который не запускается.
ARG TARGETARCH
ARG GCLOUD_VERSION=583.0.0

RUN set -eux; \
    case "${TARGETARCH:-amd64}" in \
      amd64) GC_ARCH=x86_64 ;; \
      arm64) GC_ARCH=arm ;; \
      *) echo "неподдерживаемая архитектура: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    apk add --no-cache p7zip python3; \
    wget -qO /tmp/gcloud.tar.gz \
      "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${GCLOUD_VERSION}-linux-${GC_ARCH}.tar.gz"; \
    tar zxf /tmp/gcloud.tar.gz -C /usr/local; \
    rm /tmp/gcloud.tar.gz; \
    ln -s /usr/local/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud; \
    ln -s /usr/local/google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil; \
    gcloud --version
