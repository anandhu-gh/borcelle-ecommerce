#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# 🚀 Run our custom loader to bypass the constraint checker lock
if [ -f data_backup.json ]; then
    python load_data.py
fi