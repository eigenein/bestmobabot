FROM python:3.7
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 PYTHONOPTIMIZE=2

RUN curl -sL https://deb.nodesource.com/setup_11.x | bash -
RUN apt-get install -y nodejs

COPY requirements.txt /tmp/bestmobabot/requirements.txt
RUN pip install --no-cache-dir -r /tmp/bestmobabot/requirements.txt
COPY . /tmp/bestmobabot
RUN pip install --no-cache-dir --no-deps /tmp/bestmobabot && rm -r /tmp/bestmobabot

RUN mkdir /app && touch /app/db.sqlite3 && chown -R nobody:nogroup /app
WORKDIR /app

USER nobody:nogroup
STOPSIGNAL SIGINT
ENTRYPOINT ["bestmobabot"]
CMD ["-v"]
