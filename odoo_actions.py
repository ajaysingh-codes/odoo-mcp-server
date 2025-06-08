from odoo_connector import get_odoo_connection, ODOO_DB, ODOO_PASSWORD

def get_demo_company_domains() -> list:
    """
    Returns a list of email domains from demo companies in Odoo (tagged 'demo_company').
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return []

    try:
        # Get 'demo_company' tag ID
        tag = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            'res.partner.category',
            'search_read',
            [[("name", "=", "demo_company")]],
            {'fields': ['id'], 'limit': 1}
        )
        if not tag:
            return []
        tag_id = tag[0]['id']

        # Get demo companies
        companies = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            'res.partner',
            'search_read',
            [[("category_id", "in", [tag_id])], ['is_company', '=', True]],
            {'fields': ['email'], 'limit': 50}
        )

        domains = []
        for company in companies:
            email = company.get('email', '')
            if '@' in email:
                domain = email.split('@')[-1].strip().lower()
                domains.append(domain)
        return domains
    except Exception as e:
        print(f"Error fetching demo company domains: {e}")
        return []


def create_crm_lead(lead_name: str, company_name: str = None, contact_name: str = None, email: str = None, phone: str = None, description: str = "", tags: list = None) -> dict:
    """Create a new CRM lead in Odoo."""
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "message": "Failed to connect to Odoo."}

    tag_ids = []
    if tags:
        for tag in tags:
            existing = models.execute_kw(
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                'res.partner.category',
                'search_read',
                [[("name", "=", tag)]],
                {'fields': ['id'], 'limit': 1}
            )
            if existing:
                tag_ids.append(existing[0]['id'])
            else:
                tag_id = models.execute_kw(
                    ODOO_DB,
                    uid,
                    ODOO_PASSWORD,
                    'res.partner.category',
                    'create',
                    [{"name": tag}]
                )
                tag_ids.append(tag_id)
    
    lead_data = {
        "name": lead_name,
        "type": "lead",
        "partner_name": company_name,
        "contact_name": contact_name,
        "email_from": email,
        "phone": phone,
        "description": description,
        "tag_ids": [(6, 0, tag_ids)] if tag_ids else None
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

def update_crm_lead(lead_email: str, updates: dict) -> dict:
    """
    Updates an existing lead in Odoo CRM based on the lead's email.

    Args:
        lead_email (str): Email used to find the lead.
        updates (dict): Dictionary of fields to update.

    Returns:
        dict: Result of the operation with success status and message.
    """
    uid, models = get_odoo_connection()
    if not uid or not models:
        return {"success": False, "message": "Failed to connect to Odoo."}
    
    try:
        lead_ids = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "crm.lead",
            "search",
            [[("email_from", "=", lead_email)]]
        )

        if not lead_ids:
            return {"success": False, "message": f"Lead with email {lead_email} not found."}

        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "crm.lead",
            "write",
            [lead_ids, updates]
        )

        return {"success": True, "message": f"Lead with email {lead_email} updated successfully."}
    except Exception as e:
        return {"success": False, "message": str(e)}