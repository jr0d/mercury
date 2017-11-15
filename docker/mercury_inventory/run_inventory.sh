#!/bin/bash

MERCURY_LOG_ARGS=""

if [ -n "${MERCURY_LOG_LEVEL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-level ${MERCURY_LOG_LEVEL}"
fi

if [ -n "${MERCURY_ASYNCIO_DEBUG}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --asyncio-debug ${MERCURY_ASYNCIO_DEBUG}"
fi

if [ -n "${MERCURY_INVENTORY_DB_SERVERS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-db-servers ${MERCURY_INVENTORY_DB_SERVERS}"
fi

if [ -n "${MERCURY_INVENTORY_DB_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-db-name ${MERCURY_INVENTORY_DB_NAME}"
fi

if [ -n "${MERCURY_INVENTORY_DB_REPLICA_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-db-replica-name ${MERCURY_INVENTORY_DB_REPLICA_NAME}"
fi

if [ -n "${MERCURY_INVENTORY_DB_COLLECTION}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-db-collection ${MERCURY_INVENTORY_DB_COLLECTION}"
fi

if [ -n "${MERCURY_INVENTORY_SERVICE_BIND_ADDRESS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --inventory-bind-address ${MERCURY_INVENTORY_SERVICE_BIND_ADDRESS}"
fi

# All variables defined via Docker-Compose Environment
mercury-inventory ${MERCURY_LOG_ARGS}

echo "Waiting for docker termination"
while true
do
	sleep 120
done
