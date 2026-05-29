import os
import sys
import django

# 🛠️ Tell Python where to find your project settings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finalProject.settings") # Adjust 'finalProject' if your main project folder name is different!

django.setup()

from django.core.management import call_command
from django.db import connection

print("🛑 Temporarily disabling PostgreSQL constraint checks...")
with connection.cursor() as cursor:
    cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
    
    print("🛰️ Loading data_backup.json...")
    call_command('loaddata', 'data_backup.json')
    
print("✨ Data loaded successfully!")