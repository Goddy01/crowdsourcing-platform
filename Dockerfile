FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

# For ALPINE
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# FOR DEBIAN
RUN /usr/bin/python3 -m venv /py && \
    /py/bin/pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home django-user && \
    apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# RUN python -m venv /py && \
#     /py/bin/pip install -r requirements.txt && \
#     adduser --disabled-password --no-create-home django-user
# RUN apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev

ENV PATH="/py/bin:$PATH"

WORKDIR /crowdsourcing-platform

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

USER django-user