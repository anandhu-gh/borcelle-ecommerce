#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# 🛠️ FORCE POSTGRESQL TO DEFER FOREIGN KEY CHECKS UNTIL THE END
echo "🛰️ Injecting data with deferred foreign keys..."
python manage.py shell -c "
from django.db import transaction, connection
with transaction.atomic():
    with connection.cursor() as cursor:
        cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
    from django.core.management import call_command
    call_command('loaddata', 'data_backup.json')
"