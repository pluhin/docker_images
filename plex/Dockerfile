FROM linuxserver/plex:latest

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Plex с готовыми точками монтирования библиотек"
LABEL org.opencontainers.image.licenses=MIT
LABEL maintainer="pluhin@gmail.com"
RUN mkdir /download && \
    mkdir /video && \
    mkdir /serials  && \
    mkdir /library && \
    mkdir /photo && \
    mkdir /cartoon && \
    mkdir /videos && \
    mkdir /RU && \
    mkdir /music