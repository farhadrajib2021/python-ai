from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Simple conversational agent - no manual session management needed!
# ADK web will handle sessions automatically
root_agent = LlmAgent(
    name="session_test_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are a helpful and friendly assistant.
    
    IMPORTANT: You can remember information from previous messages in this conversation.
    
    When the user introduces themselves or tells you their name, remember it.
    When the user asks about information from earlier in the conversation, recall it accurately.
    
    Be conversational and reference earlier context naturally.
    """,
)

print("✅ Session test agent created!")
print("🌐 Use 'adk web agent-session-adk' to test session management")
print("💡 Try:")
print("   1. Say: 'Hi, my name is Sam'")
print("   2. Ask: 'What's the capital of France?'")
print("   3. Ask: 'What's my name?' (should remember Sam!)")
