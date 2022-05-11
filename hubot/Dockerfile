
FROM node:16

ENV DEBIAN_FRONTEND "noninteractive"
ENV HUBOT_NAME "ha"
ENV HUBOT_OWNER "pluhin@gmail.com"
ENV HUBOT_DESCRIPTION "Home pet"
ENV REDIS_URL "redis://localhost/hubot"
RUN npm install -g hubot coffeescript yo generator-hubot && \
    useradd hubot -m
COPY . /home/hubot
RUN chown -R hubot:hubot /home/hubot
USER hubot
WORKDIR /home/hubot
RUN yo hubot --owner="${HUBOT_OWNER}" --name="${HUBOT_NAME}" --description="${HUBOT_DESCRIPTION}" --defaults && \
    sed -i /heroku/d ./external-scripts.json && \
    sed -i /redis-brain/d ./external-scripts.json && \
    npm install hubot-scripts && \
    npm install hubot-slack --save

CMD ./bin/hubot -n $HUBOT_NAME -a slack