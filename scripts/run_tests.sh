#!/bin/bash

set -e

TEST_CMD="tox"

pushd src/

    pushd mercury-common
    $TEST_CMD
    popd

    pushd mercury-inventory
    $TEST_CMD
    popd

    pushd mercury-rpc
    $TEST_CMD
    popd

    pushd mercury-log
    $TEST_CMD
    popd

popd

set +e
