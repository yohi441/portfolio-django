#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

git fetch origin main

local_commit=$(git rev-parse HEAD)
remote_commit=$(git rev-parse origin/main)

if [ "$local_commit" != "$remote_commit" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] New commit detected ($local_commit -> $remote_commit). Deploying..."
    ./deploy.sh
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No new commits."
fi
