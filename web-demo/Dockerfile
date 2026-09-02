# Две статические страницы для демонстраций выката.
FROM nginx:1.31-alpine

# Было `FROM nginx` без тега: и неявный latest, и образ на Debian вчетверо
# тяжелее alpine там, где отдаются два html-файла.
COPY index.html rollout.html /usr/share/nginx/html/
