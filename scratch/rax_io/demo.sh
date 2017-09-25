#!/bin/bash


export PYTHONPATH="/home/jared/git/mercury/scratch"
export ANSIBLE_SSH_ARGS="-F /home/jared/.ssh/ord1-bastion-iad3-jumper.config"
export MERCURY_URL="http://mercury.iad3.kir.kickstart.rackspace.com:9005"
export JSON_TARGETS='{"interfaces.lldp.switch_name": {"$regex": "g13-27.*"}}'

alias headshot="./headshot.sh"



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
    PROJECTION="?projection=$2"
    curl -s -X POST -d "$1" -H "Content-type: application/json" $MERCURY_URL/api/inventory/computers/query$PROJECTION | jq
}

function get_active {
    query_inventory '{"query": {"active": {"$ne": null}}}' $1  
}

