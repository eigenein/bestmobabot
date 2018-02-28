FROM ubuntu:17.10
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=/opt/bestmobabot:$PYTHONPATH

RUN mkdir -p /srv/bestmobabot
VOLUME /srv/bestmobabot
WORKDIR /srv/bestmobabot

RUN apt update && apt -y install python3.6 python3-pip
COPY . /opt/bestmobabot
RUN python3.6 -m pip install -r /opt/bestmobabot/requirements.txt

CMD ["python3.6", "-m", "bestmobabot", "-v"]
