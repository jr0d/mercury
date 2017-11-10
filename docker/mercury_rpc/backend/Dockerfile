FROM centos/python-36-centos7:1
# for lack of a better e-mail...just using a dev on the team ;)
MAINTAINER DCX Baremetal Devs <ben.meyer@rackspace.com>

ENV APP_NAME mercury-rpc
ENV SOURCE_ROOT ${HOME}/${APP_NAME}
ENV LOG_DIR /var/log/${APP_NAME}
ENV PID_DIR /var/run/${APP_NAME}
ENV MERCURY_CONFIG_DIR ${HOME}/.mercury
SHELL ["/bin/bash", "-c"]

VOLUME ${HOME}/${APP_NAME}

# switch to user in order to update the base image
USER root
# IPv6 doesn't resolve over VPN at least so force IPv4
RUN echo "ip_resolve=4" >> /etc/yum.conf
RUN yum -y update && yum -y install @development-tools fedora-packager rpmdevtools

# Create log & pid directories
RUN mkdir -p ${LOG_DIR} && chmod -R +w ${LOG_DIR} && chown -R default:root ${LOG_DIR}
RUN mkdir -p ${PID_DIR} && chmod -R +w ${PID_DIR} && chown -R default:root ${PID_DIR}

# switch back to the `default` user used for the Application by the base image
USER default
RUN pip install --upgrade pip

ADD . ${HOME}/${APP_NAME}

WORKDIR ${SOURCE_ROOT}
RUN cd src/mercury-common && pip install -r test-requirements.txt && pip install -e .
RUN cd src/${APP_NAME} && pip install -e .

RUN scripts/make_docker_configs.sh --rebuild rpc --database "mongo:27017" --inventory-router "tcp://mercury_inventory:9000" --redis-host redis --frontend-host mercury_rpc --backend-host mercury_rpc --info-address mercury_rpc
EXPOSE 9002:9002
CMD python src/mercury-rpc/mercury/rpc/backend/backend.py
