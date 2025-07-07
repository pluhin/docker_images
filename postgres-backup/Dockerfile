FROM postgres:17-alpine

RUN apk add --no-cache p7zip && \
    wget -qO /tmp/google-cloud-cli.tar.gz https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-524.0.0-linux-x86_64.tar.gz && \
    tar zxvf /tmp/google-cloud-cli.tar.gz -C /usr/local && \
    rm /tmp/google-cloud-cli.tar.gz && \
    ln -s /usr/local/google-cloud-cli/bin/gcloud /usr/local/bin/gcloud
