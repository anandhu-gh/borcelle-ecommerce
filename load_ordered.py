import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalProject.settings')
django.setup()

from django.core.management import call_command

# Load in strict dependency order, one file at a time
# Each loaddata call completes and commits before the next starts
fixtures_in_order = [
    'auth_users.json',
    'guestapp_data.json',
    'adminapp_data.json',
    'customerapp_data.json',
    'deliveryapp_data.json',
]

for fixture in fixtures_in_order:
    if os.path.exists(fixture):
        print(f"Loading {fixture}...")
        call_command('loaddata', fixture, verbosity=1)
        print(f"✓ {fixture} done")
    else:
        print(f"Skipping {fixture} — not found")

print("All data loaded!")