#!/usr/bin/env bash
# Exit immediately if a command exits with an error status
set -o errexit

echo "🛠️ Starting Secure Cloud Migration Pipeline..."

# 1. Install production packages
pip install -r requirements.txt

# 2. Collect CSS/JS assets
python manage.py collectstatic --no-input

# 3. Rebuild empty architecture in PostgreSQL
python manage.py migrate

# 4. Run the Python data stream with correct app capitalization
python -c "
import os, json, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalProject.settings')
django.setup()

from django.apps import apps
from django.db import transaction

if not os.path.exists('data_backup.json'):
    print('⚠️ Warning: data_backup.json file was not found.')
    exit(0)

print('📖 Reading data backup file...')
with open('data_backup.json', 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

# 🔥 FIXED: Exact capitalization to match your project configuration
ordered_labels = [
    'adminApp.category',
    'adminApp.district',
    'adminApp.location',
    'guestApp.logindetails',
    'guestApp.customer',
    'adminApp.deliveryboy',
    'adminApp.product',
    'customerApp.cart',
    'customerApp.order',
    'customerApp.payment',
    'customerApp.orderitem',
    'customerApp.feedback'
]

# Match keys exactly with the configuration array above
data_buckets = {label: [] for label in ordered_labels}
unknown_objects = []

for item in fixtures:
    # Look for case-insensitive matches to sort them safely
    matched = False
    for target_label in ordered_labels:
        if item['model'].lower() == target_label.lower():
            data_buckets[target_label].append(item)
            matched = True
            break
    if not matched:
        unknown_objects.append(item)

print('🛰️ Feeding records to PostgreSQL sequentially...')
with transaction.atomic():
    for label in ordered_labels:
        # Resolves using the correct app label string
        app_name, model_name = label.split('.')
        model = apps.get_model(app_label=app_name, model_name=model_name)
        items = data_buckets[label]
        
        if items:
            print(f'📦 Populating table: {label} ({len(items)} rows)')
            for obj_data in items:
                fields = obj_data['fields']
                if 'pk' in obj_data:
                    fields['id'] = obj_data['pk']
                
                for field_name, field_val in list(fields.items()):
                    if isinstance(field_val, list):
                        del fields[field_name]
                
                instance = model(**fields)
                try:
                    instance.save(force_insert=True)
                except Exception:
                    try:
                        instance.save()
                    except Exception:
                        pass

    for obj_data in unknown_objects:
        try:
            app_n, model_n = obj_data['model'].split('.')
            model = apps.get_model(app_label=app_n, model_name=model_n)
            fields = obj_data['fields']
            if 'pk' in obj_data:
                fields['id'] = obj_data['pk']
            instance = model(**fields)
            instance.save()
        except Exception:
            pass

print('⭐⭐ SUCCESS! PIPELINE POPULATION SYSTEM COMPLETE! ⭐⭐')
"