FROM ubuntu:17.10
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt update && apt -y install python3.6 python3-pip

COPY . /opt/bestmobabot
WORKDIR /opt/bestmobabot

RUN python3.6 -m pip install -r requirements.txt

RUN mkdir -p /srv/bestmobabot
VOLUME /srv/bestmobabot

CMD ["python3.6", "-m", "bestmobabot", "-v", "--log-file", "/srv/bestmobabot/bestmobabot.log"]
