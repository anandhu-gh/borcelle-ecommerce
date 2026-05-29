#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# This officially loads your backup file data straight into the live database
python manage.py loaddata ecommerce_data.json