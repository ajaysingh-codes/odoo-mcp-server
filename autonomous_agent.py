'''
from serper_search import search_google_profiles
from odoo_actions import create_crm_lead
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def mcp_autonomous_lead_generator(company: str, role: str = "product manager") -> list:
    """
    Takes a company and role, searches for relevant leads, enriches them via LLM,
    and creates them in Odoo CRM using create_crm_lead.
    
    Args:
        company (str): Company name
        role (str): Role title (default: 'product manager')
    
    Returns:
        list: A list of created lead summaries
    """
    query = f'site:linkedin.com/in "{role}" "{company}"'
    results = search_google_profiles(query)

    enrichment_prompt = f"""
    Given the following LinkedIn profile information, enrich each with:
    - name
    - title
    - location
    - inferred timezone
    - working hours
    - working style (e.g. remote, hybrid, in-person)
    - best time to send email
    - personal note

    Results:\n          
    {results}
    """

    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    enriched_results = anthropic_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1000,
        temperature=1,
        system="""You are an AI lead enrichment assistant. 
        Given search result snippets for professionals (e.g., from Google), extract structured lead data.

        For each entry:
        - Extract: full name, job title, company, location
        - Infer: timezone, working hours (e.g., 9am–5pm local), work style (remote/hybrid/in-person), best time to email
        - Create: a one-sentence personal note from interests/posts/snippet clues

        Respond in JSON format: a list of enriched lead dictionaries.
        """,
        messages=[
            {"role": "user", "content": enrichment_prompt}
        ]
    )

    print(enriched_results.content)

    responses = []
    for entry in enriched_results.content:
        lead_title = f"{entry['name']} from {company}"
        description = (
            f"Title: {entry['title']}. Timezone: {entry['timezone']}. "
            f"Hours: {entry['working_hours']}. Style: {entry['style']}. "
            f"Best time: {entry['best_time']}. Notes: {entry['note']}"
        )
        result = create_crm_lead(
            lead_name=lead_title,
            company_name=company,
            contact_name=entry['name'],
            email=None,
            phone=None,
            description=description
        )
        responses.append(result)

    return responses

mcp_autonomous_lead_generator("Google")

'''
    