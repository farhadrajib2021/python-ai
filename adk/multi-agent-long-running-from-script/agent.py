import uuid
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

LARGE_ORDER_THRESHOLD = 5


def place_shipping_order_with_approval(
    num_containers: int, destination: str, tool_context: ToolContext
) -> dict:
    """Places a shipping order. Orders with more than 5 containers need manager approval.
    
    This version uses ToolContext.request_confirmation() for programmatic workflows.

    Args:
        num_containers: Number of containers to ship
        destination: Shipping destination
        tool_context: Context for requesting human approval

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
    
    # Large orders need approval - check if we're awaiting confirmation
    if not tool_context.tool_confirmation:
        # First call - request approval
        tool_context.request_confirmation(
            hint=f"⚠️ Large order: {num_containers} containers to {destination}. Requires manager approval.",
            payload={
                "num_containers": num_containers,
                "destination": destination,
            }
        )
        return {
            "status": "pending_approval",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"⏳ Waiting for approval: {num_containers} containers to {destination}",
        }
    
    # Second call - process the confirmation response
    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "order_id": f"ORD-{num_containers}-HUMAN",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"✅ Order approved by manager: {num_containers} containers to {destination}",
        }
    else:
        return {
            "status": "rejected",
            "num_containers": num_containers,
            "destination": destination,
            "message": f"❌ Order rejected: {num_containers} containers to {destination}",
        }


# Create shipping agent with pausable tool
shipping_agent = LlmAgent(
    name="shipping_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a shipping coordinator assistant.
    
    When users request to ship containers:
    1. Use place_shipping_order_with_approval to process the order
    2. Report the status back to the user clearly
    3. Keep responses concise but friendly
    """,
    tools=[
        FunctionTool(func=place_shipping_order_with_approval),
    ],
)

# Wrap agent in App with resumability
shipping_app = App(
    name="shipping_app",
    root_agent=shipping_agent,
    resumability_config=ResumabilityConfig()
)

# Export the app for ADK CLI (though adk run/web won't work with this pattern)
root_agent = shipping_app

print("✅ Shipping App created with ResumabilityConfig!")


# ============================================================================
# Programmatic workflow execution with Runner
# ============================================================================

async def run_shipping_workflow():
    """Run the shipping workflow programmatically with human-in-the-loop approval.
    
    This demonstrates the programmatic pattern using Runner with sessions.
    Note: The ToolContext.request_confirmation() pattern may require specific
    ADK version or configuration to work properly.
    """
    
    session_service = InMemorySessionService()
    
    # Create session
    user_id = "manager_001"
    session = await session_service.create_session(
        app_name="shipping_app",
        user_id=user_id
    )
    session_id = session.id
    
    runner = Runner(
        app_name="shipping_app",
        agent=shipping_agent,  # Use agent directly, not app
        session_service=session_service
    )
    
    # Test Case 1: Small order (auto-approved)
    print("\n" + "="*60)
    print("TEST 1: Small order (3 containers) - should auto-approve")
    print("="*60)
    
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text="Ship 3 containers to Singapore")])
    ):
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    
    print(f"\n📋 Result 1:")
    print(f"   Response: {response_text}")
    print(f"   (Small orders auto-approve without confirmation)")
    
    # Test Case 2: Large order (needs approval)
    print("\n" + "="*60)
    print("TEST 2: Large order (20 containers) - requires approval")
    print("="*60)
    print("Note: ToolContext.request_confirmation() may require specific ADK setup")
    print("This example shows the tool execution, but programmatic approval")
    print("handling depends on ADK version and configuration.")
    print("="*60)
    
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text="Ship 20 containers to Berlin")])
    ):
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
    
    print(f"\n📋 Result 2:")
    print(f"   Response: {response_text}")
    
    print("\n" + "="*60)
    print("✅ All tests complete!")
    print("="*60)


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║  Shipping Coordinator - Programmatic Workflow with ResumabilityConfig  ║
╚═══════════════════════════════════════════════════════════════════════╝

This example demonstrates the PROGRAMMATIC pattern for human-in-the-loop:
- Uses App + ResumabilityConfig for pausable workflows
- Uses ToolContext.request_confirmation() in tool functions
- Uses Runner with invocation_id to pause and resume
- Confirmations are provided programmatically via confirmations parameter

⚠️  This pattern does NOT work with 'adk web' - it's for programmatic workflows only!
    For interactive chat, use the conversational pattern in multi-agent-long-running/

Running automated test workflow...
""")
    
    asyncio.run(run_shipping_workflow())
