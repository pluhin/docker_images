FROM ubuntu:24.04
LABEL maintainer="pluhin@gmail.com"

ENV TZ=Europe/Amsterdam DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt upgrade -yqq && \
    apt install -yqq \
      locales language-pack-ru \
      mc vim curl wget git telnet netcat-openbsd \
      gpg gnupg2 ca-certificates \
      software-properties-common lsb-release \
      convmv && \
    locale-gen en_US.UTF-8 ru_RU.UTF-8 && \
    update-locale LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8

ENV LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru

RUN printf "alias ls='ls -N --show-control-chars --color=auto'\n" > /etc/profile.d/ls-utf8.sh

RUN apt-get autoremove -yqq && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
           /usr/share/man /usr/share/doc /usr/share/doc-base
