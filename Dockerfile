# Use the specified Python 3.10 image based on Alpine
FROM python:3.10-alpine

# Set environment variable to ensure Python outputs everything to stdout
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt

COPY . .

WORKDIR /crowdsourcing-platform

EXPOSE 8000

COPY ./scripts /scripts


# Install necessary packages and set up the environment
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
        linux-headers \
        postgresql-client \
        python3-dev \
        nginx \
        build-base \
        postgresql-dev \
        gcc \
    && python3 -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --requirement /requirements.txt && \
    adduser -D -G nginx -u 1001 django-user && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /vol/web/static /vol/web/media && \
    chown -R django-user:nginx /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts /requirements.txt

ENV PATH="/scripts:/py/bin:$PATH"

# Set the user to django-user
USER django-user

# Define the default command to run the application
# CMD ["run.sh"]
CMD ["uwsgi", "--socket", ":9000", "--workers", "4", "--master", "--enable-threads", "--module", "crowdsourcing.wsgi"]