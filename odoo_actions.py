from odoo_connector import get_odoo_connection, ODOO_DB, ODOO_PASSWORD

def get_company_by_email_domain(email: str) -> dict:
    """
    Check if the given email domain belongs to any known company in Odoo.

    Args:
        email (str): The email address to check.

    Returns:
        dict: { success: bool, partner: {...} or message/error }
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "error": "Failed to connect to Odoo"}

    try:
        domain = email.split("@")[-1]
        results = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'search_read',
            [[['email', 'ilike', f'%@{domain}']]],
            {'fields': ['id', 'name', 'email'], 'limit': 1}
        )
        if results:
            return {"success": True, "partner": results[0]}
        else:
            return {"success": False, "message": "No matching company found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

from odoo_connector import get_odoo_connection, ODOO_DB, ODOO_PASSWORD

def get_assigned_salesperson_from_domain(email: str) -> int:
    """
    Given an email, finds the related company by domain and returns the assigned salesperson's user_id.
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return None

    try:
        domain = email.split('@')[-1].lower()
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[['email', 'ilike', f'%@{domain}']]],
            {'fields': ['id', 'name', 'user_id'], 'limit': 1}
        )
        if partners and partners[0].get("user_id"):
            return partners[0]["user_id"][0]  # user_id = [id, name]
        return None
    except Exception as e:
        print(f"[Error] while fetching salesperson from domain: {e}")
        return None

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

    # 🧠 Auto-assign if salesperson is tied to email domain
    if email and '@' in email:
        assigned_user_id = get_assigned_salesperson_from_domain(email)
        if assigned_user_id:
            lead_data['user_id'] = assigned_user_id
            lead_data['priority'] = '2'  # mark as high-priority

    lead_data = {k: v for k, v in lead_data.items() if v is not None}

    try:
        lead_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, "crm.lead", "create", [lead_data])
        return {
            "success": True, 
            "lead_id": lead_id,
            "assigned": bool(lead_data.get("user_id")),
            "message": f"Lead '{lead_name}' created and assigned." if lead_data.get("user_id") else f"Lead '{lead_name}' created."}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_project_tasks(project_name: str, max_tasks: int = 5) -> dict:
    """
    Retrieves a list of tasks for a specified project from Odoo.

    Args:
        project_name (str): The exact name of the project in Odoo.
        max_tasks (int, optional): Max number of tasks to return. Default is 5.

    Returns:
        dict: Includes 'success' status, 'tasks' list, and optional error messages.
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "message": "Failed to connect to Odoo."}

    try:
        project_ids = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.project",
            'search',
            [[("name", "=", project_name)]],
            {'limit': 1}
        )

        if not project_ids:
            return {"success": False, "error": f"Project '{project_name}' not found."}

        task_fields = ['name', 'user_ids', 'date_deadline', 'priority', 'description']
        tasks = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "project.task",
            "search_read",
            [[("project_id", "in", project_ids)]],
            {
                "fields": task_fields,
                "limit": max_tasks,
            }
        )

        return {
            "success": True, 
            "project_name": project_name,
            "project_id": project_ids[0],
            "tasks_retrieved": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_lead_by_email_with_classification(email: str, classification: dict, assign_salesperson: bool = False) -> dict:
    """
    Update a lead in Odoo by email with BANT classification and optionally assign a salesperson.

    Args:
        email (str): Email of the lead (email_from field).
        classification (dict): Claude's classification result.
        assign_salesperson (bool): Whether to assign current user to the lead.

    Returns:
        dict: Success/failure message and lead ID (if found).
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "error": "Failed to connect to Odoo"}

    try:
        # 1. Search for the lead by email
        lead_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'search',
            [[('email_from', '=', email)]],
            {'limit': 1}
        )

        if not lead_ids:
            return {"success": False, "error": f"No lead found with email {email}"}

        lead_id = lead_ids[0]

        # 2. Format the classification into notes
        classification_text = "\n".join([f"{k}: {v}" for k, v in classification.items()])
        values = {
            'description': f"BANT Classification:\n{classification_text}",
            'type': 'opportunity' if classification.get("is_qualified") else 'lead',
        }

        if assign_salesperson:
            values['user_id'] = uid

        # 3. Update the lead
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'crm.lead', 'write',
            [[lead_id], values]
        )

        return {"success": result, "lead_id": lead_id, "message": "Lead updated." if result else "Update failed."}

    except Exception as e:
        return {"success": False, "error": str(e)}
