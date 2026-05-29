#!/usr/bin/env bash
# exit on error
set -o errexit

# Install your Python packages
pip install -r requirements.txt

# Collect static files (CSS/Images) into the staticfiles directory
python manage.py collectstatic --no-input

# Automatically apply migrations to your persistent SQLite database
python manage.py migrate