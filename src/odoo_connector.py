import os
from dotenv import load_dotenv
import xmlrpc.client

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD_OR_API_KEY")

def get_odoo_connection():
    """Establish and return an authenticated connection to the Odoo ERP instance."""
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        if uid:
            return uid, models
        else:
            print("❌ Failed to authenticate with Odoo.")
            return None, None
    except Exception as e:
        print("❌ Connection error:", e)
        return None, None