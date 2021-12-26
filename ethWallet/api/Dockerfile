FROM python:3.8
WORKDIR /home/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /home/app/requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install netcat supervisor -y

RUN apt-get clean; rm

COPY . /home/app
COPY ./config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
