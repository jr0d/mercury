FROM ubuntu:17.10

MAINTAINER DCX Baremetal Devs <baremetal@rackspace.com>

ENV HOME /root
ENV APP_NAME mercury-backend-queue
ENV SOURCE_ROOT ${HOME}/${APP_NAME}
ENV LOG_DIR /var/log/${APP_NAME}
ENV PID_DIR /var/run/${APP_NAME}
ENV MERCURY_CONFIG_DIR ${HOME}/.mercury
ENV MY_VENV ${HOME}/venv
ENV MY_VENV_ACTIVATION ${MY_VENV}/bin/activate
SHELL ["/bin/bash", "-c"]

VOLUME ${HOME}/${APP_NAME}

RUN apt-get -qq update && apt-get -qq upgrade && apt-get install -qqy \
    git-core \
    libev4 \
    libev-dev \
    libffi-dev \
    libssl-dev \
    python3.6-dev \
    python3-pip \
    python3-setuptools \
	python-virtualenv

RUN virtualenv -p `which python3.6` ${MY_VENV}

# Create log & pid directories
RUN source ${MY_VENV_ACTIVATION} && mkdir -p ${LOG_DIR} && chmod -R +w ${LOG_DIR} && chown -R root:root ${LOG_DIR}
RUN source ${MY_VENV_ACTIVATION} && mkdir -p ${PID_DIR} && chmod -R +w ${PID_DIR} && chown -R root:root ${PID_DIR}

# upgrade pip and setuptools within the virtualenv
RUN source ${MY_VENV_ACTIVATION} && pip install --upgrade pip setuptools

ADD . ${HOME}/${APP_NAME}

WORKDIR ${SOURCE_ROOT}

# install everything into the virtualenv
RUN source ${MY_VENV_ACTIVATION} && cd ./tests && pip install -r test_requirements.txt
RUN source ${MY_VENV_ACTIVATION} && cd ./src && pip install -e . 
#EXPOSE 9000:9000
# and run it
CMD source ${MY_VENV_ACTIVATION} && mercury-backend-queue

