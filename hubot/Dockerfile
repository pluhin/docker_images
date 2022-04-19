FROM node:latest
LABEL maintener="pluhin@gmail.com"
ENV HUBOT_OWNER "Siarhei"
ENV HUBOT_NAME "hassi"
ENV HUBOT_DESCRIPTION "Home pet"
ENV EXTERNAL_SCRIPTS=hubot-diagnostics,hubot-help,hubot-google-images,hubot-google-translate,hubot-pugme,hubot-maps,hubot-rules,hubot-shipit
RUN useradd hubot -m && \
    npm install -g hubot coffeescript yo generator-hubot
USER hubot
WORKDIR /home/hubot
RUN yo hubot --owner="${HUBOT_OWNER}" --name="${HUBOT_NAME}" --description="${HUBOT_DESCRIPTION}" --defaults && \
    sed -i /heroku/d ./external-scripts.json && \
	sed -i /redis-brain/d ./external-scripts.json && \
    npm install hubot-scripts &&  \
    npm install hubot-slack --save
VOLUME ["/home/hubot/scripts"]
CMD node -e "console.log(JSON.stringify('$EXTERNAL_SCRIPTS'.split(',')))" > external-scripts.json && \
	npm install $(node -e "console.log('$EXTERNAL_SCRIPTS'.split(',').join(' '))") && \
    bin/hubot -n $HUBOT_NAME --adapter slack