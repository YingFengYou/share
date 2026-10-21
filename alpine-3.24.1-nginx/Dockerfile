FROM alpine:3.24.1

LABEL org.opencontainers.image.title="alpine-nginx" \
      org.opencontainers.image.description="Nginx on Alpine Linux 3.24.1" \
      org.opencontainers.image.base.name="alpine:3.24.1"

RUN apk upgrade --no-cache \
    && apk add --no-cache nginx \
    && mkdir -p /run/nginx \
    && chown -R nginx:nginx /var/lib/nginx /var/log/nginx /run/nginx

EXPOSE 80

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]
