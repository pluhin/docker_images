FROM node:latest

LABEL maintener="pluhin@gmail.com"

RUN useradd hubot -m && \
    npm install -g hubot coffeescript yo generator-hubot

USER hubot

WORKDIR /home/hubot

RUN yo hubot --owner="${HUBOT_OWNER}" --name="${HUBOT_NAME}" --description="${HUBOT_DESCRIPTION}" --defaults &&\
    npm install hubot-scripts &&  \
    npm install hubot-slack --save

VOLUME ["/home/hubot/scripts"]

CMD bin/hubot -n $HUBOT_NAME --adapter slack