# lts вместо latest: latest — это weekly-сборка Jenkins, она выходит
# каждую неделю и ломает плагины чаще, чем приносит нужное.
FROM jenkins/jenkins:lts

LABEL maintainer="pluhin@gmail.com"
ARG DEBIAN_FRONTEND=noninteractive

## install plugins
RUN jenkins-plugin-cli --plugins ssh-slaves \
		ansible \
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
		docker-workflow \
		job-dsl
USER jenkins
