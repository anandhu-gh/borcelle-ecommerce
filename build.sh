#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [ -f data_backup.json ]; then
    python load_ordered.py
fi