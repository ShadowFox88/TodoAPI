#!/bin/bash
set -e

# Check if the PROXY environment variable is set
if [[ ! "$PROXY" ]]; then
    echo "PROXY environment variable is not set. Exiting."
    exit 1
fi

# Check if the PROCESSES environment variable is set
if [[ ! "$PROCESSES"]]; then
    echo "PROCESSES environment variable is not set. Exiting"
    exit 1
fi


# Runs the FastAPI server with the proxy flag to support reverse proxies.
if [[ "$PROXY" == "true" ]]; then
    echo "Starting server with proxy"
    exec "fastapi run /todoapi/main/server.py --proxy-headers --port 88 --processes $PROCESSES"
else
    echo "Starting server without proxy"
    exec "fastapi run /todoapi/main/server.py --port 88 --processes $PROCESSES"
fi