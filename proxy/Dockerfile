FROM nginxinc/nginx-unprivileged:1.24.0-bullseye

LABEL maintainer="toshirothe3rd.vercel.app"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh



ENV LISTEN_PORT=8000
ENV APP_HOST=crowdsourcing-platform
ENV APP_PORT=9000

USER root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y nginx && \
    mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    mkdir -p /vol/media && \
    chmod 755 /vol/media && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /vol/static /vol/media

USER nginx

CMD ["nginx", "-g", "daemon off;"]