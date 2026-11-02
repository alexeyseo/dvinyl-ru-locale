# Dockerfile — русская локаль поверх официального образа DVinyl
#
# Собирается как обычный образ:
#   docker build -t dvinyl:ru .
#
# Затем в своём docker-compose.yml замените образ на dvinyl:ru (см. docker-compose.example.yml).
#
# Аргумент UPSTREAM позволяет взять другую версию, не правя файл:
#   docker build --build-arg UPSTREAM=ghcr.io/kyonew/dvinyl:3.3.1 -t dvinyl:ru .
ARG UPSTREAM=ghcr.io/kyonew/dvinyl:3.3.0
FROM ${UPSTREAM}

# Локаль — новый файл: обновления апстрима её не касаются.
COPY locales/ru.json /app/locales/ru.json

# Восемь точек регистрации. Скрипт идемпотентный и падает с понятным сообщением,
# если апстрим переписал строку, в которую врезается патч.
COPY apply-ru-locale.js /tmp/apply-ru-locale.js
RUN node /tmp/apply-ru-locale.js && rm /tmp/apply-ru-locale.js
