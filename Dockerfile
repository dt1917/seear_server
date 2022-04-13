FROM python:3.8-slim-buster

RUN mkdir -p /app

WORKDIR /app
ADD . /app/

RUN pip install -r requirements.txt

CMD [ "flask", "run"]