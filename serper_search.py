# serper_search.py

import os 
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_google_profiles(query: str) -> dict:
    """
    Searches Serper.dev with the given query and returns top Google search results.

    Args:
        query (str): Google-style search query, e.g. 'site:linkedin.com/in "product manager" Stripe'

    Returns:
        list[dict]: A list of search results with title, snippet, and link
    """
    if not SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY not found in environment variables")
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    params = {
        "q": query
    }
    response = requests.post(url, headers=headers, json=params)
    if response.status_code != 200:
        raise RuntimeError(f"Serper.dev error: {response.status_code} - {response.text}")

    data = response.json()
    results = data.get("organic", [])

    return [
        {
            "title": result.get("title", ""),
            "snippet": result.get("snippet", ""),
            "link": result.get("link", "")
        }
        for result in results
    ]

