#!/bin/bash

set -e

BUILD_CMD="python setup.py bdist_egg bdist_wheel upload"

pushd src/

    pushd mercury-common
    tox -r
    $BUILD_CMD
    popd

    pushd mercury-inventory
    tox -r
    $BUILD_CMD
    popd

    pushd mercury-rpc
    tox -r
    $BUILD_CMD
    popd

    pushd mercury-log
    tox -r
    $BUILD_CMD
    popd

popd

set +e
