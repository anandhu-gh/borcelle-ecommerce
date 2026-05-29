#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Load data if the file exists in your repository
if [ -f db_data.json ]; then
    python manage.py loaddata db_data.json
fi