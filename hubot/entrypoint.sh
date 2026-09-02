#!/bin/sh
set -eu

if [ -n "${EXTRA_PACKAGES:-}" ]; then
  echo "Installing extra packages..."
  # shellcheck disable=SC2046
  npm install --save $(echo "$EXTRA_PACKAGES" | tr ',' ' ')
fi

echo "Installing packages from external-scripts.json ..."
# shellcheck disable=SC2046
npm install --save $(tr -d '",[]' < ./external-scripts.json)

HUBOT_VERSION=$(grep 'hubot":' ./package.json | awk -F " " '{print $2}' | tr -d ',^"')

# Аргументы по умолчанию задаются здесь, а не в CMD. В exec-форме CMD
# переменные не раскрываются, и прежний CMD ["--name", "$HUBOT_NAME", ...]
# передавал боту буквальную строку "$HUBOT_NAME" вместо имени. Здесь есть
# shell, поэтому подстановка работает; свои аргументы, если их передать,
# перекрывают умолчания целиком.
if [ "$#" -eq 0 ]; then
  set -- --name "${HUBOT_NAME:-robot}" --adapter "${HUBOT_ADAPTER:-slack}"
fi

echo "Starting ${HUBOT_NAME:-robot} (Hubot $HUBOT_VERSION) ..."
exec bin/hubot "$@"
