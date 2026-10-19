#!/bin/sh
set -eu

STARTED_AT="$(date +%s)"

sed \
    -e "s/__BACKEND_NAME__/${BACKEND_NAME}/g" \
    -e "s/__STARTED_AT__/${STARTED_AT}/g" \
    /template/index.template.html \
    > /usr/share/nginx/html/index.html

echo "$(date -Iseconds) INFO Avvio backend ${BACKEND_NAME}"
echo "$(date -Iseconds) INFO Timestamp iniziale ${STARTED_AT}"
echo "$(date -Iseconds) INFO Avvio NGINX"

exec nginx -g 'daemon off;'