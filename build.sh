#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install production driver requirements
pip install -r requirements.txt

# 2. Collect CSS/JS assets
python manage.py collectstatic --no-input

# 3. Build the table architecture inside Render PostgreSQL
python manage.py migrate

# 4. 🔥 THE EASY FIX: Load your data rows directly inside the cloud context
if [ -f data_backup.json ]; then
    echo "📦 Found data backup! Importing rows into PostgreSQL..."
    python manage.py loaddata data_backup.json
    echo "⭐⭐ DATA IMPORT COMPLETE! ⭐⭐"
fi