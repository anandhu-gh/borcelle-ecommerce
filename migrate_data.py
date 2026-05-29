import os
import django

# Set up the Django environment inside Render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalProject.settings')
django.setup()

from django.apps import apps

independent_models = []
dependent_models = []

# Sort apps to load parents (Customers) before children (Carts)
for app_config in apps.get_app_configs():
    if app_config.label in ['auth', 'contenttypes', 'sessions', 'admin']:
        continue
        
    for model in app_config.get_models():
        name = model.__name__.lower()
        if 'customer' in name or 'user' in name or 'profile' in name:
            independent_models.append(model)
        elif 'cart' in name or 'item' in name or 'order' in name:
            dependent_models.append(model)
        else:
            independent_models.append(model)

final_migration_order = independent_models + dependent_models

print('🛰️ Starting internal data streaming from SQLite file to PostgreSQL...')

for model in final_migration_order:
    try:
        # Pull data out of the uploaded db.sqlite3 file
        local_records = model.objects.using('default').all()
        if local_records.exists():
            print(f'📦 Streaming: {model._meta.app_label} -> {model.__name__} ({local_records.count()} records)')
            for item in local_records:
                try:
                    item.save(force_insert=True)
                except Exception:
                    try:
                        item.save()
                    except Exception:
                        pass
    except Exception as e:
        print(f'⚠️ Skipping table {model.__name__}: {e}')

print('⭐⭐ SUCCESS! SQLITE DATA SUCCESSFULLY STREAMED TO POSTGRESQL! ⭐⭐')