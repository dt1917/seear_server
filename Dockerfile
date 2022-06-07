FROM python:3.8-slim-buster

RUN mkdir -p /app

WORKDIR /app
ADD . /app/

RUN apt-get update
RUN apt-get install -y libglib2.0-0 libgl1-mesa-glx libsm6 libxrender1 libxext6
RUN pip install -r requirements.txt

ENV HOST 0.0.0.0
EXPOSE 5000

CMD [ "flask", "run","--host=0.0.0.0","--port=5000"]