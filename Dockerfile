FROM python:3.10-bullseye

WORKDIR /crowdsourcing-platform

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]