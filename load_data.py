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

    SKIP_APPS = {'sessions', 'admin', 'contenttypes', 'auth'}

    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")

        with transaction.atomic():
            for entry in data:
                # Add a broad layer of protection for every single row
                try:
                    app_label, model_name = entry['model'].split('.')
                    if app_label in SKIP_APPS:
                        continue
                    
                    model = apps.get_model(app_label, model_name)
                    fields = entry['fields']
                    pk = entry['pk']
                    
                    instance, created = model.objects.get_or_create(pk=pk)
                    
                    for field_name, field_value in fields.items():
                        try:
                            field = model._meta.get_field(field_name)
                            if field.is_relation and field.many_to_one:
                                setattr(instance, f"{field_name}_id", field_value)
                            else:
                                setattr(instance, field_name, field_value)
                        except:
                            continue
                    
                    instance.save()
                except Exception as e:
                    # If this specific row fails (like the null-constraint error), 
                    # we print it and keep going!
                    print(f"⚠️ Skipping problematic row for {entry.get('model')}: {e}")
                
    print("⭐⭐ DATABASE SYNC ATTEMPT COMPLETED! ⭐⭐")

if __name__ == '__main__':
    load_fixtures_safely()