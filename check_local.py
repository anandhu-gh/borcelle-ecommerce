import os
import sqlite3

print("🔍 Checking your local db.sqlite3 file...\n")

if not os.path.exists('db.sqlite3'):
    print("❌ ERROR: No 'db.sqlite3' file found in this directory!")
    print(f"Current Directory is: {os.getcwd()}")
else:
    file_size = os.path.getsize('db.sqlite3')
    print(f"📁 Found db.sqlite3 file ({file_size / 1024:.2f} KB)")
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n--- APP TABLES WITH DATA FOUND ---")
        found_data = False
        
        for t in tables:
            table_name = t[0]
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            
            # Highlight your custom app data rows (skipping internal django logs)
            if count > 0 and not table_name.startswith(('django_', 'auth_', 'sqlite_')):
                print(f"📊 Table: {table_name} | 🎉 Rows found: {count}")
                found_data = True
                
        if not found_data:
            print("⚪ Your custom tables are completely empty or don't exist yet.")
            
    except Exception as e:
        print(f"❌ Error reading database: {e}")
    finally:
        conn.close()