#!/bin/bash

REBUILD=0

SCRIPT_ARGS=""
for ARG in ${@}
do
    case "${ARG}" in
        "--rebuild")
            REBUILD=1
            ;;
        *)
            SCRIPT_ARGS="${SCRIPT_ARGS} ${ARG}"
            ;;
    esac
done

if [ ${REBUILD} -eq 1 ]; then
    pip install PyYAML
fi

python scripts/make_docker_configs.py ${SCRIPT_ARGS}
