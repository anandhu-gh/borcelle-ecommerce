#!/usr/bin/env bash
# Exit immediately if a command exits with an error status
set -o errexit

echo "🛠️ Starting Secure Cloud Migration Pipeline..."

# 1. Install production packages
pip install -r requirements.txt

# 2. Collect static asset templates
python manage.py collectstatic --no-input

# 3. Create schema tables inside Render's PostgreSQL
python manage.py migrate

# 4. Trigger our isolated data stream file safely
python cloud_migrate.py

# 5. 🔥 THE FINAL TOUCH: Reset database ID sequences so Django can read/write data
echo "🔄 Synchronizing PostgreSQL primary key sequences..."
python manage.py sqlsequencereset adminApp guestApp customerApp | python manage.py dbshell
echo "⭐⭐ SYSTEM ONLINE AND FULLY OPERATIONAL! ⭐⭐"