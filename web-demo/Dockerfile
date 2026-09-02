# Две статические страницы для демонстраций выката.
FROM nginx:1.31-alpine

# Метка source привязывает пакет в GHCR к этому репозиторию — без неё на
# странице пакета висит «Link this package to a repository». Зачем в
# Dockerfile, а не только в CI — в README.
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
LABEL org.opencontainers.image.description="Две статические страницы для демонстрации выката"
LABEL org.opencontainers.image.licenses=MIT

# Было `FROM nginx` без тега: и неявный latest, и образ на Debian вчетверо
# тяжелее alpine там, где отдаются два html-файла.
COPY index.html rollout.html /usr/share/nginx/html/
