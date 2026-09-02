# docker_images

[![Build](https://github.com/pluhin/docker_images/actions/workflows/build.yaml/badge.svg)](https://github.com/pluhin/docker_images/actions/workflows/build.yaml)
[![Scan](https://github.com/pluhin/docker_images/actions/workflows/scan.yaml/badge.svg)](https://github.com/pluhin/docker_images/actions/workflows/scan.yaml)

Образы для домашнего кластера и подручных задач. Публикуются в `ghcr.io/pluhin/<имя>`,
доступны без авторизации.

Один каталог — один образ. Каталог с `Dockerfile` попадает в сборку сам, ничего
регистрировать вручную не нужно.

## Образы

| Образ | База | Опубликовано |
|---|---|---|
| [`ansible`](#ansible) | `alpine:3.24` | [![version](https://ghcr-badge.egpl.dev/pluhin/ansible/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/ansible) [![size](https://ghcr-badge.egpl.dev/pluhin/ansible/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/ansible) |
| [`busy-box`](#busy-box) | `ubuntu:26.04` | [![version](https://ghcr-badge.egpl.dev/pluhin/busy-box/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/busy-box) [![size](https://ghcr-badge.egpl.dev/pluhin/busy-box/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/busy-box) |
| [`cat-detector`](#cat-detector) | `python:3.12-slim` | [![version](https://ghcr-badge.egpl.dev/pluhin/cat-detector/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/cat-detector) [![size](https://ghcr-badge.egpl.dev/pluhin/cat-detector/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/cat-detector) |
| [`curl`](#curl) | `alpine:3.24` | [![version](https://ghcr-badge.egpl.dev/pluhin/curl/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/curl) [![size](https://ghcr-badge.egpl.dev/pluhin/curl/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/curl) |
| [`cyta-balance-scraper`](#cyta-balance-scraper) | `python:3.12-slim` | [![version](https://ghcr-badge.egpl.dev/pluhin/cyta-balance-scraper/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/cyta-balance-scraper) [![size](https://ghcr-badge.egpl.dev/pluhin/cyta-balance-scraper/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/cyta-balance-scraper) |
| [`hubot`](#hubot) | `node:24-alpine` | [![version](https://ghcr-badge.egpl.dev/pluhin/hubot/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/hubot) [![size](https://ghcr-badge.egpl.dev/pluhin/hubot/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/hubot) |
| [`jenkins`](#jenkins) | `jenkins/jenkins:lts` | [![version](https://ghcr-badge.egpl.dev/pluhin/jenkins/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/jenkins) [![size](https://ghcr-badge.egpl.dev/pluhin/jenkins/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/jenkins) |
| [`plex`](#plex) | `linuxserver/plex:latest` | [![version](https://ghcr-badge.egpl.dev/pluhin/plex/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/plex) [![size](https://ghcr-badge.egpl.dev/pluhin/plex/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/plex) |
| [`web-demo`](#web-demo) | `nginx:1.31-alpine` | [![version](https://ghcr-badge.egpl.dev/pluhin/web-demo/latest_tag?trim=major&label=version)](https://github.com/pluhin/docker_images/pkgs/container/web-demo) [![size](https://ghcr-badge.egpl.dev/pluhin/web-demo/size?label=size&color=blue)](https://github.com/pluhin/docker_images/pkgs/container/web-demo) |

## Как собирается

Всё делает один workflow, [`build.yaml`](.github/workflows/build.yaml), и у него три повода запуска.

**Пуш в `master`.** Собираются только каталоги, файлы в которых изменились.
Теги: `latest` и `sha-<7 знаков>`. Первый — то, что тянут развёртывания,
второй — неизменяемая запись, к которой можно вернуться.

**Тег в git — релиз.** Схема `<образ>/v<semver>`:

```bash
git tag cyta-balance-scraper/v1.2.3
git push origin cyta-balance-scraper/v1.2.3
```

Соберётся один образ и получит четыре тега: `1.2.3`, `1.2`, `1` и `latest` —
чтобы потребитель сам выбирал, насколько крепко пиниться.

Разделитель — косая черта, а не дефис: в именах `busy-box` и
`cyta-balance-scraper` дефисы уже есть, и `busy-box-v1.2.3` пришлось бы
разбирать угадыванием. Двоеточие, которое обещал прежний README
(`jenkins:v1.2.3`), в именах git-тегов запрещено вовсе, так что сборка по тегу
никогда и не работала.

**Вручную.** Actions → Build → Run workflow. Пустое поле каталога означает
«собрать все».

## Проверка на уязвимости

Trivy стоит в двух местах.

**В сборке**, между сборкой и публикацией. Образ сначала грузится в локальный
демон, сканируется и только потом уходит в реестр — публиковать непроверенное
незачем, а сканировать по ссылке в реестре значит уже опубликовать.

Порог — **CRITICAL, для которого есть исправление**. `MEDIUM` и `HIGH`
всегда только сообщаются: половина образов здесь стоит на чужих базах —
`jenkins/jenkins`, `linuxserver/plex` — и `HIGH` в них есть почти
всегда независимо от нашего кода. Сборка, падающая каждый раз, не защищает, а
приучает отключать проверку.

Но и `CRITICAL` останавливает публикацию не у всех образов, и это не
поблажка. Запрет на публикацию пересобранного образа уязвимость не убирает: в
реестре остаётся прежний образ — старше и с тем же набором проблем плюс всё,
что нашли с момента его выпуска. Для обёртки над чужой базой такой запрет
означает лишь «`latest` перестал обновляться», то есть делает хуже. Смысл
гейт имеет там, где зависимости наши и находку можно закрыть в этом же
репозитории.

Поэтому блокировка включается файлом `.trivy-blocking` в каталоге образа.
Сейчас он есть у `cyta-balance-scraper` и `cat-detector` — двух образов со
своим `requirements.txt`. Остальные сканируются так же подробно, но находки
уходят во вкладку Security и в еженедельную сводку.

Исключения по конкретным CVE — в [`.trivyignore`](.trivyignore), один файл на
репозиторий.

**По расписанию**, [`scan.yaml`](.github/workflows/scan.yaml), по понедельникам.
Уязвимости находят и после выпуска: образ, собранный в январе и с тех пор не
менявшийся, к весне обрастает CVE, и ни один push об этом не скажет — push'ей
нет. Этот прогон смотрит на теги `latest`, лежащие в реестре, и пишет в Slack
только если нашёл критическое. В тишине молчит: еженедельное «всё хорошо»
через месяц перестают читать.

## Привязка пакетов к репозиторию

На странице пакета в GHCR по умолчанию висит «Link this package to a
repository»: нет readme, нет ссылки на исходники, нет списка участников.
Связь делается не в настройках, а меткой в самом образе —
`org.opencontainers.image.source` с адресом репозитория. GHCR читает её при
публикации и привязывает пакет сам.

Метка стоит в двух местах, и это не дублирование от невнимательности. В
[`build.yaml`](.github/workflows/build.yaml) она добавляется вместе с
`revision` и `title`, которые известны только в CI. В `Dockerfile` — чтобы
связь появлялась и у образа, собранного руками:

```
LABEL org.opencontainers.image.source=https://github.com/pluhin/docker_images
```

Там же `description` — именно он показывается на странице пакета под
названием, — и `licenses`.

## Локальная сборка

```bash
docker build -t ansible ./ansible
```

## Секреты

| Секрет | Зачем | Обязателен |
|---|---|---|
| `CR_PAT` | Пуш в ghcr.io | Да, пока пакеты не выдадут репозиторию Actions-доступ |
| `SLACK_WEBHOOK` | Уведомления о сборках и находках | Нет, без него шаг пропускается |

`GITHUB_TOKEN` одного не хватает: пакеты, заведённые вне этого репозитория,
доступны ему на запись только после того, как сам пакет выдаст репозиторию
доступ. Иначе пуш падает с `denied: permission_denied: write_package` уже
после успешной сборки.

## Про cat-detector

Образ оставлен, но в работе не используется: детектор снят 28.08.2026 — за
неделю он не нашёл на кадрах ни одного животного, только людей. Код и история
целы, если появится камера, реально смотрящая туда, где ходят коты. Если
возвращаться не планируется, каталог стоит удалить — он занимает время сборки
и попадает в еженедельную проверку.

## Подробности по образам

### ansible

Ansible и ansible-lint, чтобы прогнать плейбук не устанавливая его на машину.

База: `alpine:3.24`

```bash
docker pull ghcr.io/pluhin/ansible:latest
```

### busy-box

Отладочный контейнер: mc, vim, curl, git, telnet, netcat, русские локали.

База: `ubuntu:26.04`

```bash
docker pull ghcr.io/pluhin/busy-box:latest
```

### cat-detector

YOLOv4 поверх кадров с камер. **Снят с эксплуатации** — см. ниже.

База: `python:3.12-slim`

```bash
docker pull ghcr.io/pluhin/cat-detector:latest
```

### curl

curl, wget, jq, bash — сходить по HTTP из кластера и разобрать ответ.

База: `alpine:3.24`

```bash
docker pull ghcr.io/pluhin/curl:latest
```

### cyta-balance-scraper

Забирает балансы SIM-карт Cyta через Playwright и отдаёт их по HTTP.

База: `python:3.12-slim`

```bash
docker pull ghcr.io/pluhin/cyta-balance-scraper:latest
```

### hubot

Hubot со slack-адаптером.

База: `node:24-alpine`

```bash
docker pull ghcr.io/pluhin/hubot:latest
```

### jenkins

Jenkins с предустановленным набором плагинов.

База: `jenkins/jenkins:lts`

```bash
docker pull ghcr.io/pluhin/jenkins:latest
```

### plex

Plex с заранее созданными точками монтирования библиотек.

База: `linuxserver/plex:latest`

```bash
docker pull ghcr.io/pluhin/plex:latest
```

### web-demo

Две статические страницы для демонстрации выката.

База: `nginx:1.31-alpine`

```bash
docker pull ghcr.io/pluhin/web-demo:latest
```

---

Бэйджи версии и размера отдаёт сторонний сервис `ghcr-badge.egpl.dev`: GHCR
своего эндпоинта для этого не даёт. Если он перестанет отвечать, сломаются
только картинки в этом файле.
