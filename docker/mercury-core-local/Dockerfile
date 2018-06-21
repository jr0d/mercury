FROM python
WORKDIR /

ENV SOURCE_ROOT /usr/src/mercury

RUN mkdir -p ${SOURCE_ROOT}

ADD ./src/ ${SOURCE_ROOT}
RUN cd ${SOURCE_ROOT} && pip install -e .

