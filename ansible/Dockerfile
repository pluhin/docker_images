# Ansible под рукой: запустить плейбук, не ставя его на машину.
FROM alpine:3.24

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Ansible и ansible-lint для запуска плейбуков из контейнера"
LABEL org.opencontainers.image.licenses=MIT
LABEL maintainer="pluhin@gmail.com"

# Ветка Alpine закреплена вместо latest. С latest образ, собранный сегодня и
# полгода назад, отличается мажорной версией ansible, а воспроизводимость
# держится только до следующего релиза Alpine. Обновление ветки — отдельный
# коммит, который видно в истории.
#
# apk update убран: с --no-cache индекс и так скачивается свежим, а лишний
# слой оставался в образе.
RUN apk add --no-cache ansible ansible-lint sshpass
