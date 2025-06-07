import gradio as gr
from odoo_actions import create_crm_lead, get_project_tasks

def mcp_create_odoo_lead(lead_title: str, company: str = None, contact: str = None,
                          email_address: str = None, phone_number: str = None, notes: str = "") -> dict:
    """
    Creates a new lead in the Odoo CRM system.
    """
    return create_crm_lead(
        lead_name=lead_title,
        company_name=company,
        contact_name=contact,
        email=email_address,
        phone=phone_number,
        description=notes
    )

def mcp_get_odoo_tasks(project_name: str, number_of_tasks: int = 5) -> dict:
    """
    Retrieves a list of tasks for a specified Odoo project.

    Args:
        project_name (str): Name of the project in Odoo.
        number_of_tasks (int): Max number of tasks to retrieve (default: 5).

    Returns:
        dict: success flag, project info, list of tasks, or error message.
    """
    return get_project_tasks(project_name, max_tasks = number_of_tasks)

lead_creator_tool_iface = gr.Interface(
    fn=mcp_create_odoo_lead,
    inputs=[
        gr.Text(label="Lead Title"),
        gr.Text(label="Company Name"),
        gr.Text(label="Contact Name"),
        gr.Text(label="Email Address"),
        gr.Text(label="Phone Number"),
        gr.Text(label="Notes", lines=3),
    ],
    outputs=gr.JSON(label="Response"),
    title="Create CRM Lead",
    description="Create a new lead in the Odoo CRM system.",
)

task_fetcher_tool_iface = gr.Interface(
    fn=mcp_get_odoo_tasks,
    inputs=[gr.Text(label="Project Name"), gr.Number(label="Number of Tasks", value=5)],
    outputs=gr.JSON(label="Task List"),
    title="Odoo Project Task Fetcher (MCP Tool)",
    description="Fetch tasks for a given Odoo project. Exposed as an MCP tool.",
    allow_flagging="never"
)

if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("# Odoo MCP Tools")
        with gr.Tab("Create CRM Lead"):
            lead_creator_tool_iface.render()
        with gr.Tab("Get Project Tasks"):
            task_fetcher_tool_iface.render()
    
    demo.launch(mcp_server=True, server_name="0.0.0.0", share=False)
