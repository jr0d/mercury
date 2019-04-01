FROM python:3.7
WORKDIR /

ADD src/ /usr/src/mercury
RUN pip install -r /usr/src/mercury/requirements.txt
RUN cd /usr/src/mercury && pip install -e .


