# Hubot со slack-адаптером.
FROM node:24-alpine

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
