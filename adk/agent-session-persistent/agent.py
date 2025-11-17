from typing import Any, Dict
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types

print("✅ ADK components imported successfully.")

# Retry configuration for the model
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Define helper functions that will be reused throughout the notebook
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    print(f"\n ### Session: {session_name}")

    # Get app name from the Runner
    app_name = runner_instance.app_name

    # Attempt to create a new session or retrieve an existing one
    try:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
        print(f"   📝 Created new session")
    except Exception as e:
        session = await session_service.get_session(
            app_name=app_name, session_id=session_name, user_id=USER_ID
        )
        # Count messages in history
        history = session.state.get("history", []) if isinstance(session.state, dict) else []
        print(f"   📂 Retrieved existing session (has {len(history)} messages)")

    # Process queries if provided
    if user_queries:
        # Convert single query to list for uniform processing
        if type(user_queries) == str:
            user_queries = [user_queries]

        # Process each query in the list sequentially
        for query in user_queries:
            print(f"\n👤 User > {query}")

            # Convert the query string to the ADK Content format
            query = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream the agent's response asynchronously
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query
            ):
                # Check if the event contains valid content
                if event.content and event.content.parts:
                    # Filter out empty or "None" responses before printing
                    if (
                        event.content.parts[0].text != "None"
                        and event.content.parts[0].text
                    ):
                        print(f"🤖 {MODEL_NAME} > ", event.content.parts[0].text)
    else:
        print("No queries!")


print("✅ Helper functions defined.")

APP_NAME = "persistent_chat_app"  # Application name
USER_ID = "demo_user"  # User ID
SESSION = "demo_session"  # Session ID

MODEL_NAME = "gemini-2.5-flash-lite"


# Step 1: Create the agent with LlmAgent
root_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="text_chat_bot",
    description="A text chatbot with persistent memory",
    instruction="You are a helpful and friendly assistant. Remember context from the conversation.",
)

# Step 2: Switch to DatabaseSessionService
# SQLite database will be created automatically in the current directory
db_path = Path(__file__).parent / "my_agent_data.db"
db_url = f"sqlite:///{db_path}"  # Local SQLite file
session_service = DatabaseSessionService(db_url=db_url)

# Step 3: Create the Runner with persistent storage
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

print("✅ Stateful agent initialized with PERSISTENT storage!")
print(f"   - Application: {APP_NAME}")
print(f"   - User: {USER_ID}")
print(f"   - Database: {db_path}")
print(f"   - Using: {session_service.__class__.__name__}")
print(f"   💾 Sessions will survive restarts!")


# Main function to run the conversation demo
async def main():
    """Run a conversation demo with persistent session management."""
    
    # UNCOMMENT THIS BLOCK FOR FIRST RUN - Creates the session and introduces yourself
    print("\n" + "="*60)
    print("TEST 1: First conversation - Creating session")
    print("="*60)
    
    await run_session(
        runner,
        [
            "Hi, I am Sam! What is the capital of United States?",
            "What's my name?",  # Should remember Sam
        ],
        "persistent-session-demo",
    )
    # END OF TEST 1
    
    
    # COMMENT OUT TEST 1 ABOVE, THEN UNCOMMENT THIS BLOCK FOR SECOND RUN
    # This will prove persistence - agent remembers without re-introducing yourself!
    # print("\n" + "="*60)
    # print("TEST 2: Testing persistence - Loading existing session")
    # print("="*60)
    # print("💡 This will load the session from the database!")
    # print("💡 The agent should remember Sam WITHOUT being told again!")
    # 
    # await run_session(
    #     runner,
    #     [
    #         "What's my name?",  # Should STILL remember Sam from database!
    #         "What did you tell me about the US capital?",  # Should remember answer
    #     ],
    #     "persistent-session-demo",  # Same session ID!
    # )
    
    print("\n" + "="*60)
    print("✅ Test complete!")
    print("="*60)
    print(f"💾 All conversation data is saved in: {db_path}")
    print(f"\n� TO TEST PERSISTENCE:")
    print(f"   1. Run this script now (Test 1 is active)")
    print(f"   2. Comment out TEST 1, uncomment TEST 2")
    print(f"   3. Run again - agent will remember Sam from database!")
    print(f"   4. This proves the session persisted! 🎯")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║  Persistent Session Management Demo                       ║
╚═══════════════════════════════════════════════════════════╝

This example demonstrates:
- DatabaseSessionService with SQLite for persistent storage
- Sessions survive program restarts
- Conversation history is stored in a local database file
- Same session can be retrieved and continued later

Key difference from InMemorySessionService:
❌ InMemory: Lost when program stops
✅ Database: Saved to disk, survives restarts!

Running demo...
""")
    
    asyncio.run(main())
