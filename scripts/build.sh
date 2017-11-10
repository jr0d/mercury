#!/bin/bash

set -e

BUILD_CMD="python setup.py bdist_egg bdist_wheel upload"

pushd src/

    pushd mercury-common
    tox
    $BUILD_CMD
    popd

    pushd mercury-inventory
    tox
    $BUILD_CMD
    popd

    pushd mercury-rpc
    tox
    $BUILD_CMD
    popd

    pushd mercury-log
    tox
    $BUILD_CMD
    popd

popd

set +e
