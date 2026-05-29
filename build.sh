#!/usr/bin/env bash
# Exit immediately if a command exits with an error status
set -o errexit

echo "🛠️ Starting Secure Cloud Migration Pipeline..."

# 1. Install production requirements
pip install -r requirements.txt

# 2. Collect static asset templates
python manage.py collectstatic --no-input

# 3. Create schema tables inside Render's PostgreSQL
python manage.py migrate

# 4. Trigger our isolated data stream file safely
python cloud_migrate.py