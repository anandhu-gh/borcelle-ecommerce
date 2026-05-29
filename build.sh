#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# This line injects your data into Render's database automatically
python manage.py loaddata cloud_data.json