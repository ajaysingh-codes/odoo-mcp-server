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

    
    
