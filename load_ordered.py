import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalProject.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("Disabling FK constraints for data load...")

with connection.cursor() as cursor:
    cursor.execute('SET session_replication_role = replica;')

print("Loading fixture...")
call_command('loaddata', 'data_backup.json', verbosity=2)

with connection.cursor() as cursor:
    cursor.execute('SET session_replication_role = DEFAULT;')

print("FK constraints re-enabled. Done!")