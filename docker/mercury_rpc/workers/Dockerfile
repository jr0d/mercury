FROM centos/python-35-centos7:3.5
# for lack of a better e-mail...just using a dev on the team ;)
MAINTAINER DCX Baremetal Devs <ben.meyer@rackspace.com>

ENV APP_NAME mercury-rpc
ENV SOURCE_ROOT ${HOME}/${APP_NAME}
ENV LOG_DIR /var/log/${APP_NAME}
ENV PID_DIR /var/run/${APP_NAME}
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

# TODO: Add config file
# TODO: Add log configuration file
# TODO: Run the application
