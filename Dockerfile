FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

# For ALPINE
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt /requirements.txt

RUN pip freeze > requirements.txt

COPY ./scripts /scripts

COPY . .
# FOR DEBIAN
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y linux-headers-generic && \
    apt-get install -y python3-venv python3-dev python-dev && \
    apt-get install -y nginx && \
    /usr/bin/python3 -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --requirement /requirements.txt && \
    adduser --disabled-password --no-create-home django-user && \
    apt-get install -y postgresql-server-dev-all gcc && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /vol/web/static /vol/web/media && \
    chmod -R +x /scripts /requirements.txt


# RUN python -m venv /py && \
#     /py/bin/pip install -r requirements.txt && \
#     adduser --disabled-password --no-create-home django-user
# RUN apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev

USER django-user

ENV PATH="/scripts:/py/bin:$PATH"

WORKDIR /crowdsourcing-platform


# RUN pip3 install -r requirements.txt


CMD ["run.sh"]

USER django-user