#!/usr/bin/env bash

WORKDIR="/home/jared/git/mercury/src"
SESSION="MERCURY"
VIRTUALENV_CMD="workon python3-mercury"
set -e

pushd  $WORKDIR

tmux -2 new-session -d -s $SESSION

tmux rename-window 'Servers'
tmux send-keys "$VIRTUALENV_CMD" C-m
tmux send-keys "pushd mercury-inventory" C-m
tmux send-keys "python mercury/inventory/server.py" C-m
tmux send-keys "popd" C-m

tmux split-window -h

tmux send-keys "$VIRTUALENV_CMD" C-m
tmux send-keys "pushd mercury-rpc" C-m
tmux send-keys "python mercury/rpc/backend/backend.py" C-m
tmux send-keys "popd" C-m

tmux select-pane -t 0
tmux split-window -v

tmux send-keys "$VIRTUALENV_CMD" C-m
tmux send-keys "pushd mercury-rpc" C-m
tmux send-keys "python mercury/rpc/frontend/frontend.py" C-m
tmux send-keys "popd" C-m

tmux select-pane -t 2
tmux split-window -v

tmux send-keys "$VIRTUALENV_CMD" C-m
tmux send-keys "pushd mercury-log" C-m
tmux send-keys "python mercury/log_service/server.py" C-m
tmux send-keys "popd" C-m

tmux new-window -t $SESSION:1 -n 'Workers'
tmux select-window -t$SESSION:1

tmux send-keys "$VIRTUALENV_CMD" C-m
tmux send-keys "pushd mercury-rpc" C-m
tmux send-keys "python mercury/rpc/workers/worker.py" C-m
tmux send-keys "popd" C-m

tmux new-window -t $SESSION:2 -n 'htop' 'htop'


tmux select-window -t $SESSION:0
tmux -2 attach-session -t $SESSION
popd

