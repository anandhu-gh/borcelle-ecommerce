import django
django.setup()

from django.core.management import call_command
from django.db import connection

print("🛑 Temporarily disabling PostgreSQL constraint checks...")
with connection.cursor() as cursor:
    # This completely halts foreign key validation across PostgreSQL for this session
    cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
    
    print("🛰️ Loading data_backup.json...")
    call_command('loaddata', 'data_backup.json')
    
print("✨ Data loaded successfully! Re-enforcing security...")