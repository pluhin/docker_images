# Hubot со slack-адаптером.
FROM node:24-alpine

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Hubot со slack-адаптером"
LABEL org.opencontainers.image.licenses=MIT

# Было library/node:lts-alpine. Ветка закреплена явно: lts переезжает на новый
# мажор раз в год, и образ менял среду выполнения сам по себе.
ENV HUBOT_NAME=robot \
    HUBOT_ADAPTER=slack \
    HUBOT_HOME=/home/hubot

# ENV HUBOT_VERSION 3.3.2 убран: значение нигде не использовалось, а
# entrypoint всё равно читает настоящую версию из package.json. Заодно ушёл
# устаревший синтаксис ENV через пробел, на который ругается buildkit.

ARG HUBOT_OWNER="Siarhei Pishchyk <pluhin@gmail.com>"
ARG HUBOT_DESCRIPTION="Hubot robot. Born to serve."

RUN npm install -g coffeescript yo generator-hubot@next

RUN addgroup -g 501 hubot && \
    adduser -D -h $HUBOT_HOME -u 501 -G hubot hubot

WORKDIR $HUBOT_HOME
USER hubot

RUN yo hubot --no-insight \
             --adapter="$HUBOT_ADAPTER" \
             --owner="$HUBOT_OWNER" \
             --name="$HUBOT_NAME" \
             --description="$HUBOT_DESCRIPTION" \
             --defaults

# Леса убираются сразу после стройки. yo и generator-hubot нужны ровно на
# одну команду выше, а оставались в готовом образе вместе со своим деревом
# зависимостей — и все четыре критических находки Trivy были именно там:
#
#   generator-hubot/node_modules/lodash      2.4.2   исправлен в 4.17.12 (2019)
#   generator-hubot/node_modules/decompress  1.0.7   исправлен в 4.2.1
#   generator-hubot/node_modules/form-data   2.3.3   исправлен в 2.5.4
#   yo/node_modules/locutus                  2.0.39  исправлен в 3.0.14
#
# Обновить их нельзя: версии прибиты внутри самих генераторов, а те давно не
# обновлялись — lodash 2.4.2 при доступной 4.17.12 говорит сам за себя. Зато
# можно не тащить генераторы в рантайм: entrypoint их не трогает, ему нужны
# только npm и bin/hubot.
#
# coffeescript остаётся: hubot-скрипты бывают на нём, а критических там нет.
USER root
RUN npm uninstall -g yo generator-hubot && npm cache clean --force
USER hubot

COPY --chown=hubot:hubot entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

# CMD с аргументами убран намеренно. Было:
#     CMD ["--name", "$HUBOT_NAME", "--adapter", "slack"]
# Exec-форма не раскрывает переменные, поэтому в bin/hubot приходила строка
# из семи символов "$HUBOT_NAME", и бот всё это время запускался именно с
# таким именем. Значения по умолчанию теперь подставляет entrypoint, где для
# этого есть shell; передать свои аргументы по-прежнему можно — они просто
# перекроют умолчания.
ENTRYPOINT ["./entrypoint.sh"]
