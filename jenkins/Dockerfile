# lts вместо latest: latest — это weekly-сборка Jenkins, она выходит
# каждую неделю и ломает плагины чаще, чем приносит нужное.
FROM jenkins/jenkins:lts

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Jenkins LTS с предустановленным набором плагинов"
LABEL org.opencontainers.image.licenses=MIT

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
