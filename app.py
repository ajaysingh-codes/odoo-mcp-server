import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import gradio as gr

from odoo_actions import (
    create_crm_lead,
    get_project_tasks,
    update_lead_by_email_with_classification,
    get_company_by_email_domain,
)

load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")


def mcp_create_odoo_lead(lead_title: str, company: str = None, contact: str = None,
                          email_address: str = None, phone_number: str = None, notes: str = "") -> dict:
    """
    Creates a new lead in the Odoo CRM system. 
    This tool should be used **only if the company or contact does not already exist** in the CRM.
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
    """Retrieves a list of tasks for a specified project from Odoo."""
    return get_project_tasks(project_name, max_tasks=number_of_tasks)

def mcp_classify_and_update_lead(email_text: str, email_address: str) -> dict:
    """
    Classifies a lead using Claude (BANT) and updates the lead in Odoo by email address.

    Args:
        email_text (str): The lead's email message or request text.
        email_address (str): The email of the lead (used to find them in Odoo).

    Returns:
        dict: Classification result and Odoo update result.
    """
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    prompt = f"""
    You are a sales assistant trained in the BANT methodology.

    Classify this lead by providing:
    - lead_type: "Qualified Buyer", "Job Applicant", "Investor", "Researcher", or "Other"
    - budget, authority, need, and timeline (BANT)
    - is_qualified: true/false

    Lead Email/Text:
    \"\"\"
    {email_text}
    \"\"\"

    Respond in JSON format like:
    {{
    "lead_type": "...",
    "budget": "...",
    "authority": "...",
    "need": "...",
    "timeline": "...",
    "is_qualified": true
    }}
    """

    try:
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=800,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Ensure response.content is valid and extract text from the first block
        if not response.content or not isinstance(response.content, list) or len(response.content) == 0:
            raise ValueError("Claude response content is empty or not in the expected list format.")
        
        first_block = response.content[0]
        if not hasattr(first_block, 'text'):
            # This case might occur if the block type is not 'text' (e.g., 'image')
            raise ValueError("Claude response's first content block does not have a 'text' attribute.")
            
        raw_json_string = first_block.text

        # Clean potential markdown code block fences, as per MEMORY[209c25eb-2762-449b-bb96-8ff6ecfeff4e]
        if raw_json_string.startswith("```json\n") and raw_json_string.endswith("\n```"):
            raw_json_string = raw_json_string[len("```json\n"):-len("\n```")]
        elif raw_json_string.startswith("```") and raw_json_string.endswith("```"): # A simpler check for just backticks
            raw_json_string = raw_json_string[len("```"):-len("```")]
        
        # Strip any leading/trailing whitespace that might interfere with JSON parsing
        raw_json_string = raw_json_string.strip()
        
        # For debugging, you might want to print the string that will be parsed:
        print(f"Attempting to parse JSON: '{raw_json_string}'") 

        classification = json.loads(raw_json_string)
    except Exception as e:
        # Consider logging the raw_json_string here if parsing fails for further debugging
        # e.g., import logging; logging.error(f"Failed to parse JSON. String was: '{raw_json_string if 'raw_json_string' in locals() else 'unavailable'}' Error: {e}")
        return {"success": False, "error": f"Claude call or JSON parsing failed: {e}"}

    # Update the lead using email
    result = update_lead_by_email_with_classification(email_address, classification, assign_salesperson)

    return {
        "success": result.get("success", False),
        "claude_classification": classification,
        "odoo_result": result,
        "assign_salesperson": assign_salesperson,
        "matched_company": company_check.get("partner") if assign_salesperson else None
    }

# MCP Tool Interfaces
lead_creator_iface = gr.Interface(fn=mcp_create_odoo_lead, inputs=[
    gr.Textbox(label="Lead Title"),
    gr.Textbox(label="Company Name"),
    gr.Textbox(label="Contact Name"),
    gr.Textbox(label="Email Address"),
    gr.Textbox(label="Phone Number"),
    gr.Textbox(label="Notes", lines=3),
], outputs=gr.JSON(), flagging_mode="never")

task_fetcher_iface = gr.Interface(fn=mcp_get_odoo_tasks, inputs=[
    gr.Textbox(label="Project Name"),
    gr.Number(label="Number of Tasks", value=5)
], outputs=gr.JSON(), flagging_mode="never")

lead_classifier_iface = gr.Interface(
    fn=mcp_classify_and_update_lead,
    inputs=[
        gr.Text(label="Email Text"),
        gr.Text(label="Email Address")
    ],
    outputs=gr.JSON(label="Classification Result"),
    allow_flagging="never"
)

# Gradio UI/MCP server
with gr.Blocks() as demo:
    gr.Markdown("### Odoo MCP Tools")
    with gr.Tab("Create Lead"):
        lead_creator_iface.render()
    with gr.Tab("Get Tasks"):
        task_fetcher_iface.render()
    with gr.Tab("Classify and Update Lead"):
        lead_classifier_iface.render()

if __name__ == "__main__":
    demo.launch(mcp_server=True, server_name="0.0.0.0", share=False)
