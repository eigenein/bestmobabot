FROM python:3.6.5
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=/opt/bestmobabot:$PYTHONPATH
ENV PIP_NO_CACHE_DIR=off
ENV PIPENV_PIPFILE=/opt/bestmobabot/Pipfile

RUN mkdir -p /srv/bestmobabot
VOLUME /srv/bestmobabot
WORKDIR /srv/bestmobabot

RUN pip install pipenv --upgrade

COPY . /opt/bestmobabot
RUN pipenv install --deploy --system

CMD ["python", "-m", "bestmobabot", "-v"]
