FROM docker.io/library/nginx:1.30.4-alpine3.24-slim

LABEL org.opencontainers.image.title="nginx-alpine" \
      org.opencontainers.image.description="Official Nginx 1.30.4 on Alpine Linux 3.24.1 slim with pcre2 security update" \
      org.opencontainers.image.base.name="nginx:1.30.4-alpine3.24-slim"

RUN apk add --no-cache --upgrade pcre2

EXPOSE 80
