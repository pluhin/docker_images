# Подручный набор для проверок из кластера: сходить по HTTP, разобрать JSON.
FROM alpine:3.24

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="curl, wget, jq, bash для проверок из кластера"
LABEL org.opencontainers.image.licenses=MIT
LABEL maintainer="pluhin@gmail.com"

# Было `FROM alpine` вовсе без тега — тот же latest, только неявно.
# rm /var/cache/apk/* убран как бессмысленный при --no-cache: кеш не пишется.
RUN apk add --no-cache curl bash jq wget
