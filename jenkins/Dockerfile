FROM jenkins/jenkins:latest

LABEL maintainer="pluhin@gmail.com"
ARG DEBIAN_FRONTEND=noninteractive

## install plugins
RUN jenkins-plugin-cli --plugins ssh-slaves \
		ansible \
		docker-plugin \
		email-ext \
		mailer \
		greenballs \
		simple-theme-plugin \
		parameterized-trigger \
		rebuild \
		github \
		kubernetes \
		ansicolor \
		blueocean \
		stashNotifier \
		show-build-parameters \
		credentials \
		configuration-as-code \
		command-launcher \
		external-monitor-job \
		ssh-agent \
		pipeline-stage-view \
		slack \
		instant-messaging \
		global-slack-notifier \
		docker-workflow
USER root

RUN apt-get update && apt-get install -yqq apt-transport-https \
		ca-certificates \
		curl \
		gnupg2 \
        	wget \
		jq \
		python3-pip \
		software-properties-common \
	&& curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey \
    && add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
        $(lsb_release -cs) \
        stable" \
	&& pip3 install ansible \
	&& apt-get update \
	&& git config --global core.sshCommand 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' \
	&& apt-get -y install docker-ce -qq \
	&& gpasswd -a jenkins docker \
	&& usermod -a -G docker jenkins \
    && newgrp docker \
	&& echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
	&& echo "    UserKnownHostsFile=/dev/null" >> /etc/ssh/ssh_config \
    && apt-get purge --auto-remove -yqq \
	&& apt-get clean \
	&& rm -rf \
	    /var/lib/apt/lists/* \
	    /tmp/* \
	    /var/tmp/* \
	    /usr/share/man \
	    /usr/share/doc \
	    /usr/share/doc-base

USER jenkins
