import os
import sys
import sqlite3
import psycopg2

print("🚀 Starting direct over-the-air SQLite extraction...")

# 1. Connect to your local SQLite file
if not os.path.exists('db.sqlite3'):
    print("❌ Error: db.sqlite3 file not found in this directory!")
    sys.exit()

sqlite_conn = sqlite3.connect('db.sqlite3')
sqlite_cur = sqlite_conn.cursor()

# 2. Connect securely to Render PostgreSQL
try:
    pg_conn = psycopg2.connect(
        dbname="borcelle",
        user="borcelle_user",
        password="c7GGFdvsWRLgWBCGpiXwVqnMLYmIbAMA",
        host="dpg-d8cghheq1p3s73bft0j0-a.singapore-postgres.render.com",
        port="5432",
        sslmode="require"  # 🔥 Forces the secure connection Render demands
    )
    pg_cur = pg_conn.cursor()
    print("🔒 Securely connected to Render PostgreSQL database!")
except Exception as e:
    print(f"❌ Connection to Render failed: {e}")
    sys.exit()

# 3. Explicitly order your tables to respect Foreign Key constraints (Parents first, then children)
ordered_tables = [
    "adminApp_category",
    "adminApp_district",
    "adminApp_location",
    "guestApp_logindetails",
    "guestApp_customer",
    "adminApp_deliveryboy",
    "adminApp_product",
    "customerApp_cart",
    "customerApp_order",
    "customerApp_payment",
    "customerApp_orderitem",
    "customerApp_feedback"
]

# 4. Extract and stream data table by table
for table in ordered_tables:
    try:
        # Check if table exists in SQLite
        sqlite_cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        if not sqlite_cur.fetchone():
            continue

        sqlite_cur.execute(f"SELECT * FROM [{table}]")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            continue
            
        # Get table columns
        sqlite_cur.execute(f"PRAGMA table_info([{table}])")
        columns = [col[1] for col in sqlite_cur.fetchall()]
        
        print(f"📦 Extracting {len(rows)} rows from local table: {table}")
        
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        
        # ON CONFLICT DO NOTHING ensures it won't crash if you rerun the script
        insert_query = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'
        
        for row in rows:
            # Clean string encoding values dynamically to avoid transfers errors
            cleaned_row = [
                v.encode('utf-8', 'surrogateescape').decode('utf-8', 'ignore') if isinstance(v, str) else v 
                for v in row
            ]
            pg_cur.execute(insert_query, cleaned_row)
            
        pg_conn.commit()
        print(f"✅ Successfully transferred {table} -> Render PostgreSQL!")
        
    except Exception as e:
        print(f"⚠️ Could not transfer table {table}: {e}")
        pg_conn.rollback()

# Close database tunnels
sqlite_conn.close()
pg_conn.close()
print("\n⭐⭐ DEPLOYMENT EXTRACTION COMPLETE! REFRESH YOUR LIVE WEBSITE NOW! ⭐⭐")