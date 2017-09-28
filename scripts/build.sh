#!/bin/bash

set -e

BUILD_CMD="python setup.py bdist_egg bdist_wheel upload"

pushd src/
pushd mercury-agent
$BUILD_CMD

popd
pushd mercury-common
$BUILD_CMD

popd
pushd mercury-inventory
$BUILD_CMD

popd
pushd mercury-rpc
$BUILD_CMD

popd
pushd mercury-log
$BUILD_CMD
popd
popd

set +e
