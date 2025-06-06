from src.odoo_connector import get_odoo_connection

uid, models = get_odoo_connection()

if uid and models:
    print(f"✅ Connected to Odoo! UID = {uid}")
    version = models.execute_kw('odoodb', uid, 'admin', 'res.partner', 'search_read', [[]], {'limit': 1})
    print("Sample query result:", version)
else:
    print("❌ Connection to Odoo failed.")