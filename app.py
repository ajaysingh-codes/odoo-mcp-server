import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import gradio as gr
from odoo_actions import create_crm_lead, get_project_tasks, update_crm_lead, get_demo_company_domains
from claude_router import classify_lead_need
# from serper_search import search_google_profiles
# from autonomous_agent import mcp_autonomous_lead_generator

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("CLAUDE_API_KEY")

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

def mcp_update_lead(email: str, update_fields: str) -> dict:
    """
    Updates a CRM lead using their email address.

    Args:
        email (str): The email address identifying the lead.
        update_fields (str): A JSON string like '{"description": "followed up", "phone": "123456"}'.

    Returns:
        dict: Update status.
    """
    try:
        updates = json.loads(update_fields)
        return update_crm_lead(email, updates)
    except json.JSONDecodeError:
        return {"success": False, "message": "Invalid JSON format for update fields."}

'''
def mcp_search_profiles(company: str, role: str = "product manager") -> list:
    """
    Uses Serper.dev to find public LinkedIn profiles of people with the given role at the given company.

    Args:
        company (str): The target company to search (e.g., "Stripe").
        role (str, optional): The job title or role (default is "product manager").

    Returns:
        list[dict]: Search result entries with title, snippet, and link.
    """
    query = f'site:linkedin.com/in "{role}" "{company}"'
    return search_google_profiles(query)
'''

def qualify_bant_lead(email_text: str) -> dict:
    """
    Uses Claude to assess an inbound lead email and extract BANT qualification and lead type.

    Args:
        email_text (str): The raw text of the inbound email or transcript.

    Returns:
        dict: Includes `lead_type`, full BANT breakdown, `is_qualified`, and an explanation.
    """
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    system_prompt = f"""
        You are a sales qualification assistant trained in BANT methodology.
        Your task is to classify inbound leads and determine whether they are a qualified buyer or something else (e.g., job applicant, researcher, investor).

        First, determine the lead_type:
        - Qualified Buyer
        - Job Applicant
        - Researcher
        - Investor
        - Other

        Then evaluate each BANT criterion:
        - Budget: Do they mention budget or purchasing intent?
        - Authority: Are they a decision-maker or purchasing stakeholder?
        - Need: Do they clearly express a need for the product or service?
        - Timeframe: Is there a stated or implied urgency?

        Respond in the following JSON format:
        {{
        "lead_type": "Qualified Buyer",
        "BANT": {{
            "Budget": true,
            "Authority": true,
            "Need": true,
            "Timeframe": "Q3 2025"
        }},
        "is_qualified": true,
        "explanation": "Clear buying intent with urgency and decision-making authority."
        }}
        """
    
    user_prompt = f"""Here is an inbound message to analyze:

    {email_text}

    Classify the lead type and assess BANT as instructed.
    """
    try:
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1000,
            temperature=0.5,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        try:
            # Extract JSON from markdown code block if present
            response_text = response.content[0].text
            if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
                # Extract content between ```json and the next ```
                json_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
                # Try without the json specifier
                json_text = response_text.split("```", 1)[1].split("```", 1)[0].strip()
            else:
                # No code block, use the raw text
                json_text = response_text
                
            # Parse the extracted JSON
            result = json.loads(json_text)
            return result
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse Claude's response as JSON",
                "raw_response": response.content[0].text
            }
    except Exception as e:
        return {"error": str(e)}

'''
lead_generator_iface = gr.Interface(
    fn=mcp_autonomous_lead_generator,
    inputs=[
        gr.Textbox(label="Company", placeholder="e.g. Stripe"),
        gr.Textbox(label="Role", value="Product Manager")
    ],
    outputs=gr.JSON(label="Created Leads"),
    title="Autonomous Lead Generator (MCP Tool)",
    description="Searches, enriches, and creates leads from a company and role. Powered by Serper.dev + Claude + Odoo.",
    allow_flagging='never'
)
'''

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
    flagging_mode="never"
)

update_lead_tool_iface = gr.Interface(
    fn=mcp_update_lead,
    inputs=[
        gr.Text(label="Email Address"),
        gr.Text(label="Update Fields (JSON)", lines=3),
    ],
    outputs=gr.JSON(label="Response"),
    title="Update CRM Lead",
    description="Update an existing lead in the Odoo CRM system.",
)
"""
search_tool_iface = gr.Interface(
    fn=mcp_search_profiles,
    inputs=[
        gr.Textbox(label="Company", placeholder="e.g. Stripe"),
        gr.Textbox(label="Role", value="product manager")
    ],  
    outputs=gr.JSON(label="Search Results"),
    title="Search PMs at a Company (via Serper.dev)",
    description="Searches Google for public LinkedIn profiles using Serper.dev. This is used to find PMs at a target company.",
    flagging_mode='never'
)
"""

bant_qual_tool = gr.Interface(
    fn=qualify_bant_lead,
    inputs=gr.Textbox(label="Inbound Email or Transcript", lines=10),
    outputs=gr.JSON(label="BANT Qualification"),
    title="Lead Qualification Tool (BANT + Type Classifier)",
    description="Analyze a lead's email and determine if they're a qualified buyer using BANT. Claude will also classify if the sender is an investor, researcher, job applicant, etc.",
    flagging_mode='never'
)

if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("# Odoo MCP Tools")
        with gr.Tab("Create CRM Lead"):
            lead_creator_tool_iface.render()
        with gr.Tab("Get Project Tasks"):
            task_fetcher_tool_iface.render()
        with gr.Tab("Update CRM Lead"):
            update_lead_tool_iface.render()
        # with gr.Tab("Search PMs at a Company"):
        #     search_tool_iface.render()
        # with gr.Tab("Autonomous Lead Generator"):
        #     lead_generator_iface.render()
        with gr.Tab("Lead Qualification Tool"):
            bant_qual_tool.render()
    
    demo.launch(mcp_server=True, server_name="0.0.0.0", share=False)
