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
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-backend-bind-address ${MERCURY_RPC_SERVICE_BIND_ADDRESS}"
fi

if [ -n "${MERCURY_RPC_ORIGIN_NAME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-origin-name ${MERCURY_RPC_ORIGIN_NAME}"
fi

if [ -n "${MERCURY_RPC_ORIGIN_DATACENTER}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-origin-datacenter ${MERCURY_RPC_ORIGIN_DATACENTER}"
fi

if [ -n "${MERCURY_RPC_ORIGIN_PUBLIC_ADDRESS}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-origin-public-address ${MERCURY_RPC_ORIGIN_PUBLIC_ADDRESS}"
fi

if [ -n "${MERCURY_RPC_ORIGIN_FRONTEND_PORT}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-origin-frontend-port ${MERCURY_RPC_ORIGIN_FRONTEND_PORT}"
fi

if [ -n "${MERCURY_RPC_INVENTORY_ROUTER}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-inventory-router ${MERCURY_RPC_INVENTORY_ROUTER}"
fi

if [ -n "${MERCURY_RPC_PING_INTERVAL}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-ping-interval ${MERCURY_RPC_PING_INTERVAL}"
fi

if [ -n "${MERCURY_RPC_PING_CYCLE_TIME}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-ping-cycle-time ${MERCURY_RPC_PING_CYCLE_TIME}"
fi

if [ -n "${MERCURY_RPC_PING_INITIAL_TIMEOUT}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-ping-initial-timeout ${MERCURY_RPC_PING_INITIAL_TIMEOUT}"
fi

if [ -n "${MERCURY_RPC_PING_RETRIES}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-ping-retries ${MERCURY_RPC_PING_RETRIES}"
fi

if [ -n "${MERCURY_RPC_PING_BACKOFF}" ]; then
    MERCURY_LOG_ARGS="${MERCURY_LOG_ARGS} --rpc-ping-backoff ${MERCURY_RPC_PING_BACKOFF}"
fi

# All variables defined via Docker-Compose Environment
mercury-backend ${MERCURY_LOG_ARGS}

echo "Waiting for docker termination"
while true
do
	sleep 120
done
