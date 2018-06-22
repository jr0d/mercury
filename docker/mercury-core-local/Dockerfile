FROM python:3.6.5
WORKDIR /

ENV SOURCE_ROOT /usr/src/mercury

RUN mkdir -p ${SOURCE_ROOT}

ADD ./src ${SOURCE_ROOT}
RUN pip install -r ${SOURCE_ROOT}/requirements.txt
RUN pip install -r ${SOURCE_ROOT}/test-requirements.txt
RUN cd ${SOURCE_ROOT} && pip install -e . 

