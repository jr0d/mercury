#!/bin/bash


export PYTHONPATH="/home/jared/git/mercury/scratch"
export ANSIBLE_SSH_ARGS="-F /home/jared/.ssh/ord1-bastion-iad3-jumper.config"
export MERCURY_URL="http://mercury.iad3.kir.kickstart.rackspace.com:9005"
export JSON_TARGETS='{"interfaces.lldp.switch_name": {"$regex": "g13-27.*"}}'
export ALL_TARGETS='{}'
export G9='{"dmi.sys_vendor": "HP"}'
export R720='{"dmi.sys_vendor": "Dell Inc."}'

alias headshot="./headshot.sh"
alias mcli="python execution.py"


function get_status {
    curl -s $MERCURY_URL/api/rpc/jobs/$1/status | jq
}

function get_tasks {
    curl -s $MERCURY_URL/api/rpc/jobs/$1/tasks | jq
}

function get_task {
    curl -s $MERCURY_URL/api/rpc/task/$1 | jq
}

function query_inventory {
    if [ -n "$2" ]
    then
        PROJECTION="?projection=$2"
    else
        PROJECTION=""
    fi

    if [ -n "$3" ]
    then
        LIMIT="&limit=$3"
    else
        LIMIT=""
    fi

    QUERY="{\"query\": $1}"
    curl -s -X POST -d "$QUERY" -H "Content-type: application/json" $MERCURY_URL/api/inventory/computers/query$PROJECTION$LIMIT | jq
}

function get_inventory {
    if [ -n "$2" ]
    then
        PROJECTION="?projection=$2"
    else
        PROJECTION=""
    fi
    curl -s "$MERCURY_URL/api/inventory/computers/$1$PROJECTION" | jq
}


function get_active {
    query_inventory '{"active": {"$ne": null}}' $1
}


function demo_capabilities {
    python lex.py demo_capabilities
}

function create_raid
{
    python execution.py "$G9" resources/raid0_single_disk.json
}

function destroy_raid
{
    python execution.py "$G9" resources/clear_adapter_0.json
}

function deploy
{
    python press.py "$ALL_TARGETS" press/ubuntu_k8.yaml
    python execution.py "$ALL_TARGETS" resources/mount_boot.json
    python execution.py "$ALL_TARGETS" resources/kexec_ubuntu.json
}

function destroy
{
    destroy_raid
}

echo "****   Don't forget to build your inventory          ****"
echo "****   Make sure to build it on the jump host, too   ****"
