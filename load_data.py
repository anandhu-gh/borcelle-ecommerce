import os
import sys
import json
import django

# Set up environment variables
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finalProject.settings")
django.setup()

from django.apps import apps
from django.db import transaction, connection

def load_fixtures_safely():
    fixture_path = 'data_backup.json'
    if not os.path.exists(fixture_path):
        print(f"⚠️ {fixture_path} not found. Skipping data import.")
        return

    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🛑 Disabling foreign key constraints for this session...")
    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")

        # Process everything inside a single atomic block
        with transaction.atomic():
            print("🛰️ Deserializing and inserting rows safely via Django ORM...")
            
            for entry in data:
                app_label, model_name = entry['model'].split('.')
                model = apps.get_model(app_label, model_name)
                
                fields = entry['fields']
                pk = entry['pk']
                
                # Build the model instance
                instance = model(pk=pk)
                
                for field_name, field_value in fields.items():
                    field = model._meta.get_field(field_name)
                    
                    # Handle foreign keys safely by assigning the raw ID integer
                    if field.is_relation and field.many_to_one:
                        setattr(instance, f"{field_name}_id", field_value)
                    else:
                        setattr(instance, field_name, field_value)
                
                # Save via ORM (bypasses default loaddata constraint loops)
                instance.save(force_insert=True)
                
    print("⭐⭐ SUCCESS! All rows inserted cleanly into PostgreSQL! ⭐⭐")

if __name__ == '__main__':
    load_fixtures_safely()