#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

git pull --ff-only origin main

source venv/bin/activate
pip install -r requirements.txt

python manage.py collectstatic --noinput

sudo systemctl restart portfolio
