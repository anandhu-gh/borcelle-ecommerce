#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --no-input

# 3. Apply database migrations
python manage.py migrate

# 4. Load data ONLY if the file exists in your repository
if [ -f db_data.json ]; then
    echo "Data file found! Importing data into database..."
    python manage.py loaddata db_data.json
else
    echo "No data file found. Skipping data import."
fi