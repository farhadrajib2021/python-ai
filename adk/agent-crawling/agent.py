import os
import requests
from requests.auth import HTTPBasicAuth

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

# Get credentials from environment
NETRIVALS_USERNAME = os.getenv("NETRIVALS_USERNAME", "")
NETRIVALS_PASSWORD = os.getenv("NETRIVALS_PASSWORD", "")

def get_store_products(store_id: int, page: int = 1, limit: int = 100) -> dict:
    """
    Get products for a specific store from the Netrivals API.
    
    Args:
        store_id: The ID of the store to fetch products for
        page: Page number for pagination (default: 1)
        limit: Number of products per page (default: 100, max: 100)
        
    Returns:
        Dictionary containing the products data or error information
    """
    base_url = "https://endpoint.netrivals.com"
    url = f"{base_url}/v1/store/{store_id}/products"
    
    params = {
        "page": page,
        "limit": limit
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(NETRIVALS_USERNAME, NETRIVALS_PASSWORD),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "message": e.response.text if e.response else str(e)
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": "Request failed",
            "message": str(e)
        }

# Create function tool from the get_store_products function
netrivals_tool = FunctionTool(func=get_store_products)

# Create and export the agent for ADK web
root_agent = LlmAgent(
    name="netrivals_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    tools=[netrivals_tool],
    instruction=(
        "You are a helpful assistant that retrieves product information from the Netrivals API. "
        "When asked about products for a store, use the get_store_products function with the store ID. "
        "IMPORTANT: From the API response, present all product data but IGNORE and do not include "
        "the 'rival_products' field. Show all other information including product details, prices, "
        "stock, categories, and marketplace_offers. Format the data in a clear, readable way."
    ),
)

