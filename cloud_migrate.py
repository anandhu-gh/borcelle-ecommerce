import os
import json
import django
from django.db import connection

# Initialize Django environment to read database routing settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalProject.settings')
django.setup()

from django.apps import apps

def run_migration():
    if not os.path.exists('data_backup.json'):
        print('⚠️ Warning: data_backup.json file was not found.')
        return

    print('📖 Reading data backup file...')
    with open('data_backup.json', 'r', encoding='utf-8') as f:
        fixtures = json.load(f)

    # Creation hierarchy mapping
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

    data_buckets = {label: [] for label in ordered_labels}
    unknown_objects = []

    for item in fixtures:
        matched = False
        for target_label in ordered_labels:
            if item['model'].lower() == target_label.lower():
                data_buckets[target_label].append(item)
                matched = True
                break
        if not matched:
            unknown_objects.append(item)

    print('🛰️ Feeding raw rows straight into PostgreSQL engine...')
    
    # Use a direct database cursor to completely bypass Django validation
    with connection.cursor() as cursor:
        for label in ordered_labels:
            app_name, model_name = label.split('.')
            try:
                model = apps.get_model(app_label=app_name, model_name=model_name)
            except LookupError:
                continue
                
            items = data_buckets[label]
            if not items:
                continue
                
            db_table = model._meta.db_table
            print(f'📦 Injecting Raw SQL -> Table: {db_table} ({len(items)} rows)')
            
            # Identify the actual database primary key column name
            pk_column = model._meta.pk.column

            for obj_data in items:
                raw_fields = obj_data['fields']
                
                # Direct SQL column-to-value map
                sql_data = {}
                if 'pk' in obj_data:
                    sql_data[pk_column] = obj_data['pk']

                for field_name, field_val in raw_fields.items():
                    if isinstance(field_val, list):
                        continue # Skip M2M lists
                    
                    # Look up the actual database column name (handles foreign key _id suffixes)
                    try:
                        field_object = model._meta.get_field(field_name)
                        column_name = field_object.column
                        sql_data[column_name] = field_val
                    except Exception:
                        # Fallback if field name matches exactly
                        sql_data[field_name] = field_val

                # Construct a raw INSERT statement with conflict protection
                columns = list(sql_data.keys())
                values = list(sql_data.values())
                
                quoted_columns = [f'"{col}"' for col in columns]
                placeholders = [f"%s"] * len(columns)
                
                query = f'''
                    INSERT INTO "{db_table}" ({", ".join(quoted_columns)}) 
                    VALUES ({", ".join(placeholders)}) 
                    ON CONFLICT ({pk_column}) DO NOTHING;
                '''
                
                try:
                    cursor.execute(query, values)
                except Exception as e:
                    print(f'   ⚠️ Raw database insertion skipped: {e}')

if __name__ == '__main__':
    run_migration()
    print('⭐⭐ SUCCESS! RAW DATA POPULATION SYSTEM COMPLETE! ⭐⭐')