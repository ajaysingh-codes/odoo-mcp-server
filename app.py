import gradio as gr
from odoo_actions import create_crm_lead

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

lead_creator_tool = gr.Interface(
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

if __name__ == "__main__":
    lead_creator_tool.launch(mcp_server=True, server_name="0.0.0.0", share=False)
