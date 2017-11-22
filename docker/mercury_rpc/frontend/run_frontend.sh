#!/bin/bash

MERCURY_LOG_ARGS=""

if [ -n "${MERCURY_LOG_LEVEL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-level ${MERCURY_LOG_LEVEL}"
fi

if [ -n "${MERCURY_ASYNCIO_DEBUG}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --asyncio-debug ${MERCURY_ASYNCIO_DEBUG}"
fi

if [ -n "${MERCURY_SUBTASK_DEBUG}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --subtask-debug ${MERCURY_SUBTASK_DEBUG}"
fi

if [ -n "${MERCURY_RPC_DB_SERVERS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-db-servers ${MERCURY_RPC_DB_SERVERS}"
fi

if [ -n "${MERCURY_RPC_DB_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-db-name ${MERCURY_RPC_DB_NAME}"
fi

if [ -n "${MERCURY_RPC_DB_REPLICA_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-db-replica-name ${MERCURY_RPC_DB_REPLICA_NAME}"
fi

if [ -n "${MERCURY_RPC_DB_COLLECTION}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-jobs-db-collection ${MERCURY_RPC_DB_COLLECTION}"
fi

if [ -n "${MERCURY_RPC_DB_COLLECTION}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-tasks-db-collection ${MERCURY_RPC_DB_COLLECTION}"
fi

if [ -n "${MERCURY_RPC_SERVICE_BIND_ADDRESS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-frontend-bind-address ${MERCURY_RPC_SERVICE_BIND_ADDRESS}"
fi

if [ -n "${MERCURY_RPC_INVENTORY_ROUTER}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-inventory-router ${MERCURY_RPC_INVENTORY_ROUTER}"
fi

if [ -n "${MERCURY_RPC_REDIS_HOST}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-host ${MERCURY_RPC_REDIS_HOST}"
fi

if [ -n "${MERCURY_RPC_REDIS_PORT}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-port ${MERCURY_RPC_REDIS_PORT}"
fi

if [ -n "${MERCURY_RPC_REDIS_QUEUE}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-queue ${MERCURY_RPC_REDIS_QUEUE}"
fi

# All variables defined via Docker-Compose Environment
mercury-frontend ${MERCURY_LOG_ARGS}

echo "Waiting for docker termination"
while true
do
	sleep 120
done
