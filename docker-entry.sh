#!/usr/bin/env bash
set -euo pipefail

log_dir=/var/log/nmcp
mkdir -p "${log_dir}"

log_name=$(date '+%Y-%m-%d_%H-%M-%S')

nmcp-qc-serve 2>&1 | tee -a "${log_dir}/nmcp-qc-${log_name}.log"
