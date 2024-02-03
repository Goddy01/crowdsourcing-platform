FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

# For ALPINE
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# FOR DEBIAN
RUN /usr/bin/python3 -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home django-user && \
    apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev linux-headers && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R crowdsourcing:crowdsourcing /vol && \
    chmod -R +x /scripts

# RUN python -m venv /py && \
#     /py/bin/pip install -r requirements.txt && \
#     adduser --disabled-password --no-create-home django-user
# RUN apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev

USER django-user

ENV PATH="/scripts:/py/bin:$PATH"

WORKDIR /crowdsourcing-platform

COPY requirements.txt requirements.txt

COPY ./scripts /scripts

RUN pip3 install -r requirements.txt

COPY . .

CMD ["run.sh"]

USER django-user