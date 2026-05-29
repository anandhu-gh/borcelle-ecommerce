import os
import sys
import json
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finalProject.settings")
django.setup()

from django.apps import apps
from django.db import transaction, connection

def load_fixtures_safely():
    fixture_path = 'data_backup.json'
    if not os.path.exists(fixture_path):
        return

    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")

        with transaction.atomic():
            for entry in data:
                app_label, model_name = entry['model'].split('.')
                model = apps.get_model(app_label, model_name)
                
                fields = entry['fields']
                pk = entry['pk']
                
                # Get existing object or create a new one
                instance, created = model.objects.get_or_create(pk=pk)
                
                for field_name, field_value in fields.items():
                    field = model._meta.get_field(field_name)
                    if field.is_relation and field.many_to_one:
                        setattr(instance, f"{field_name}_id", field_value)
                    else:
                        setattr(instance, field_name, field_value)
                
                # Update existing records or insert new ones without crashing
                instance.save()
                
    print("⭐⭐ DATABASE SYNCED SUCCESSFULLY! ⭐⭐")

if __name__ == '__main__':
    load_fixtures_safely()