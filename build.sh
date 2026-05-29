#!/usr/bin/env bash
# Exit on any error
set -o errexit

# 1. Install lean production requirements
pip install -r requirements.txt

# 2. Collect CSS/JS files
python manage.py collectstatic --no-input

# 3. Apply blank table architecture to PostgreSQL
python manage.py migrate

# 4. Execute our migration script to stream the records
python migrate_data.py