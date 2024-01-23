FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

# For ALPINE
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# FOR DEBIAN
RUN apt-get update && apt-get install -y postgresql-server-dev-all gcc python3-dev

WORKDIR /crowdsourcing-platform

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]