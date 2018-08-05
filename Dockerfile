FROM python:3.7
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONPATH=/opt/bestmobabot:$PYTHONPATH
ENV PIP_NO_CACHE_DIR=off
ENV PIPENV_PIPFILE=/tmp/Pipfile

# Create directory for logs and state.
RUN mkdir -p /srv/bestmobabot
VOLUME /srv/bestmobabot
WORKDIR /srv/bestmobabot

# Install dependencies.
RUN apt-get update -qqy && apt-get install -qqy libopenblas-dev gfortran
RUN pip install pipenv
COPY Pipfile Pipfile.lock /tmp/
RUN pipenv install --deploy --system

# Copy the sources.
COPY . /opt/bestmobabot

# Start.
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "-m", "bestmobabot"]
CMD ["-v"]
