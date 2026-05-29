#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load fixture data into PostgreSQL safely
if [ -f data_backup.json ]; then
    python manage.py loaddata data_backup.json
fi