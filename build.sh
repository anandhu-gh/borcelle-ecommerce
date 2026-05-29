#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# 🚀 AUTOMATED LOADING: Handles all apps, regardless of order or how many you have!
python manage.py loaddata data_backup.json --ignorenonexistent