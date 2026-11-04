# Russian locale on top of an official DVinyl image.
#
#   docker build -t dvinyl:ru .
#
# Then point your compose file at dvinyl:ru (see docker-compose.example.yml).
#
# UPSTREAM takes another release without editing this file:
#   docker build --build-arg UPSTREAM=ghcr.io/kyonew/dvinyl:3.3.1 -t dvinyl:ru .
#
# This locale targets DVinyl 4.0.0. While 4.0.0 lives only on the `release/4.0.0` branch there
# is no official image to sit on top of, so use Dockerfile.source for it and keep this file for
# the releases that do have an image (3.3.0 and later).
ARG UPSTREAM=ghcr.io/kyonew/dvinyl:latest
FROM ${UPSTREAM}

# The locale is a new file: upstream updates never touch it.
COPY locales/ru.json /app/locales/ru.json

# Nineteen registration edits. The script is idempotent and fails with a readable message when
# upstream has rewritten one of the lines it cuts into.
COPY apply-ru-locale.js /tmp/apply-ru-locale.js
RUN node /tmp/apply-ru-locale.js && rm /tmp/apply-ru-locale.js
