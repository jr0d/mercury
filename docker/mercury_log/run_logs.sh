#!/bin/bash

MERCURY_LOG_ARGS=""

if [ -n "${MERCURY_LOG_LEVEL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-level ${MERCURY_LOG_LEVEL}"
fi

if [ -n "${MERCURY_LOG_SERVICE_BIND_ADDRESS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-service-bind-address ${MERCURY_LOG_SERVICE_BIND_ADDRESS}"
fi

if [ -n "${MERCURY_LOG_DB_SERVERS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-service-db-servers ${MERCURY_LOG_DB_SERVERS}"
fi

if [ -n "${MERCURY_LOG_DB_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-service-db-name ${MERCURY_LOG_DB_NAME}"
fi

if [ -n "${MERCURY_LOG_DB_COLLECTION}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-service-db-collection ${MERCURY_LOG_DB_COLLECTION}"
fi

if [ -n "${MERCURY_LOG_DB_REPLICA_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-service-db-replica-name ${MERCURY_LOG_DB_REPLICA_NAME}"
fi

# All variables defined via Docker-Compose Environment
echo "Command-line: mercury-log ${MERCURY_LOG_ARGS}"
mercury-log ${MERCURY_LOG_ARGS}

echo "Waiting for docker termination"
while true
do
	sleep 120
done
