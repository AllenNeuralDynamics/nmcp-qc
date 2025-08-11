#!/usr/bin/env bash

logName=$(date '+%Y-%m-%d_%H-%M-%S');

mkdir -p /var/log/nmcp

export PYTHONPATH=$PWD

fastapi run main.py --port 5000 >> /var/log/nmcp/nmcp-qc-${logName}.log 2>&1

# CMD ["fastapi", "run", "main.py", "--port", "5000"]
