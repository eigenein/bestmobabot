FROM python:3.7
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV APPLICATION_PATH=/opt/bestmobabot
ENV WORKING_PATH=/srv/bestmobabot
ENV PYTHONPATH=$APPLICATION_PATH:$PYTHONPATH
ENV PIP_NO_CACHE_DIR=off

# Create directory for logs and state.
RUN mkdir -p $WORKING_PATH
VOLUME $WORKING_PATH
WORKDIR $WORKING_PATH

# Install dependencies.
RUN apt-get update -qqy && apt-get install -qqy libopenblas-dev gfortran
COPY requirements.txt $APPLICATION_PATH/
RUN pip install -r $APPLICATION_PATH/requirements.txt

# Copy the sources.
COPY . $APPLICATION_PATH

# Start.
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "-m", "bestmobabot"]
CMD ["-v"]
