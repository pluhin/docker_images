# Подручный набор для проверок из кластера: сходить по HTTP, разобрать JSON.
FROM alpine:3.24
LABEL maintainer="pluhin@gmail.com"

# Было `FROM alpine` вовсе без тега — тот же latest, только неявно.
# rm /var/cache/apk/* убран как бессмысленный при --no-cache: кеш не пишется.
RUN apk add --no-cache curl bash jq wget
