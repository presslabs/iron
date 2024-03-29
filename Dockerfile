FROM python:3.5-alpine

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=django_project.settings

COPY ./requirements.txt /requirements.txt
RUN set -ex \
    && apk add --no-cache \
        make \
        mariadb-client-libs \
        openssl \
        su-exec \
    && addgroup -g 998 iron \
    && adduser -SD -u 998 -G iron -h /app iron \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev \
    && pip install --no-cache-dir -r /requirements.txt \
    && apk del .build-deps

COPY . /app
WORKDIR /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["web"]
