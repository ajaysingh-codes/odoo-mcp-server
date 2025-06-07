from odoo_connector import get_odoo_connection, ODOO_DB, ODOO_PASSWORD

def create_crm_lead(lead_name, company_name=None, contact_name=None, email=None, phone=None, description=""):
    """Create a new CRM lead in Odoo."""
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "message": "Failed to connect to Odoo."}

    lead_data = {
        "name": lead_name,
        "partner_name": company_name,
        "contact_name": contact_name,
        "email_from": email,
        "phone": phone,
        "description": description,
    }

    lead_data = {k: v for k, v in lead_data.items() if v is not None}

    try:
        lead_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "crm.lead", "create", [lead_data])
        return {"success": True, "lead_id": lead_id}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
    

    
    
