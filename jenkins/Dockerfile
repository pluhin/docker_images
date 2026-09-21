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

# То же, что в cyta-balance-scraper, и по той же причине: базовый образ
# пересобирается реже, чем Debian выпускает security-обновления. На 21.09.2026
# здесь стоял perl 5.40.1-6 при доступном 5.40.1-6+deb13u1 — три критических
# CVE, которые Trivy размножил в двенадцать алертов, потому что Debian держит
# perl в четырёх бинарных пакетах (perl, perl-base, perl-modules-5.40,
# libperl5.40) и сообщает про каждый отдельно.
#
# Обновляются все пакеты, а не перечисленные поимённо: набор меняется от
# месяца к месяцу, и список вручную означал бы возвращаться сюда после
# каждого скана.
#
# root нужен только на время обновления: образ jenkins/jenkins:lts работает
# под пользователем jenkins, и apt из-под него не запустится. Возврат к
# jenkins обязателен — без него контейнер поедет от root.
USER root
RUN apt-get update && apt-get upgrade -yqq && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
USER jenkins

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
