#!/bin/bash

MERCURY_LOG_ARGS=""

if [ -n "${MERCURY_LOG_LEVEL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --log-level ${MERCURY_LOG_LEVEL}"
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

if [ -n "${MERCURY_RPC_REDIS_HOST}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-host ${MERCURY_RPC_REDIS_HOST}"
fi

if [ -n "${MERCURY_RPC_REDIS_PORT}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-port ${MERCURY_RPC_REDIS_PORT}"
fi

if [ -n "${MERCURY_RPC_REDIS_QUEUE}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-redis-queue ${MERCURY_RPC_REDIS_QUEUE}"
fi

if [ -n "${MERCURY_RPC_WORKER_THREADS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-worker-threads ${MERCURY_RPC_WORKER_THREADS}"
fi

if [ -n "${MERCURY_RPC_WORKER_MAX_REQUESTS_PER_THREAD}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-worker-max-requests-per-thread ${MERCURY_RPC_WORKER_MAX_REQUESTS_PER_THREAD}"
fi

# All variables defined via Docker-Compose Environment
mercury-rpc-worker ${MERCURY_LOG_ARGS}

echo "Waiting for docker termination"
while true
do
	sleep 120
done
