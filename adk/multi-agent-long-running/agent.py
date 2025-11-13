from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

LARGE_ORDER_THRESHOLD = 5


def place_shipping_order(num_containers: int, destination: str) -> dict:
    """Places a shipping order. Orders with more than 5 containers need manager approval.

    Args:
        num_containers: Number of containers to ship
        destination: Shipping destination

    Returns:
        Dictionary with order status and details
    """
    
    # Small orders (≤5 containers) auto-approve
    if num_containers <= LARGE_ORDER_THRESHOLD:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-AUTO",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"✅ Order auto-approved: {num_containers} containers to {destination}",
        }
    
    # Large orders need approval
    return {
        "status": "needs_approval",
        "num_containers": num_containers,
        "destination": destination,
        "message": f"⚠️ Large order detected: {num_containers} containers to {destination}. This requires manager approval. Please ask the user to confirm.",
    }
def approve_shipping_order(num_containers: int, destination: str) -> dict:
    """Approve a large shipping order after user confirmation.

    Args:
        num_containers: Number of containers to ship
        destination: Shipping destination

    Returns:
        Dictionary with approved order details
    """
    return {
        "status": "approved",
        "order_id": f"ORD-{num_containers}-HUMAN",
        "num_containers": num_containers,
        "destination": destination,
        "message": f"✅ Order approved by manager: {num_containers} containers to {destination}",
    }


# print("✅ Long-running functions created!")

# Create shipping agent with pausable tool
shipping_agent = LlmAgent(
    name="shipping_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a shipping coordinator assistant.
  
  When users request to ship containers:
   1. Use place_shipping_order to check if the order can be processed
   2. If status is "approved", confirm the order to the user with the order ID
   3. If status is "needs_approval", inform the user that this large order requires manager approval
      and ask them: "Would you like to approve this order? (yes/no)"
   4. If user confirms approval (says yes, approve, confirm, etc.), use approve_shipping_order
   5. If user rejects (says no, reject, cancel, etc.), inform them the order was cancelled
   6. Keep responses concise but friendly
  """,
    tools=[
        FunctionTool(func=place_shipping_order),
        FunctionTool(func=approve_shipping_order)
    ],
)

# print("✅ Shipping Agent created!")

# Export the agent for ADK CLI
root_agent = shipping_agent
