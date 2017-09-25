#!/bin/bash

export PYTHONPATH="/home/jared/git/mercury/scratch"
export ANSIBLE_SSH_ARGS="-F /home/jared/.ssh/ord1-bastion-iad3-jumper.config"

alias headshot="./headshot.sh"

function get_status {
    curl -s http://mercury.iad3.kir.kickstart.rackspace.com:9005/api/rpc/jobs/$1/status | jq
}

function get_tasks {
    curl -s http://mercury.iad3.kir.kickstart.rackspace.com:9005/api/rpc/jobs/$1/tasks | jq
}

function get_task {
    curl -s http://mercury.iad3.kir.kickstart.rackspace.com:9005/api/rpc/task/$1 | jq
}
