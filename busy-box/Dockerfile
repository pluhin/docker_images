# Отладочный контейнер: залезть в кластер и посмотреть руками.
FROM ubuntu:26.04

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Отладочный контейнер: mc, vim, curl, git, telnet, netcat, русские локали"
LABEL org.opencontainers.image.licenses=MIT
LABEL maintainer="pluhin@gmail.com"

ENV TZ=Europe/Amsterdam DEBIAN_FRONTEND=noninteractive

# apt-get вместо apt: у apt нет стабильного интерфейса для скриптов, и он сам
# об этом предупреждает в каждой сборке.
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -yqq && \
    apt-get install -yqq --no-install-recommends \
      locales language-pack-ru \
      mc vim curl wget git telnet netcat-openbsd \
      gpg gnupg2 ca-certificates \
      software-properties-common lsb-release \
      convmv && \
    locale-gen en_US.UTF-8 ru_RU.UTF-8 && \
    update-locale LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8 && \
    apt-get autoremove -yqq && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
           /usr/share/man /usr/share/doc /usr/share/doc-base

ENV LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru

RUN printf "alias ls='ls -N --show-control-chars --color=auto'\n" > /etc/profile.d/ls-utf8.sh
