
FROM node:16

ENV DEBIAN_FRONTEND "noninteractive"
ENV HUBOT_NAME "hassi"
ENV HUBOT_OWNER "pluhin@gmail.com"
ENV HUBOT_DESCRIPTION "Home pet"
ENV REDIS_URL "redis://localhost/hubot"

RUN useradd hubot -m
COPY . /home/hubot
RUN chown -R hubot:hubot /home/hubot
USER hubot
WORKDIR /home/hubot
RUN npm install
CMD ./bin/hubot -n $HUBOT_NAME -a slack