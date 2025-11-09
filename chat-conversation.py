"""
Chat Conversation with Gemini
Multi-turn conversation where the AI remembers context
"""

from google import genai

# Initialize Genai client with Vertex AI authentication
# Make sure you've run: gcloud auth application-default login
client = genai.Client(
    vertexai=True,
    project="metro-markets-sms-dev",
    location="europe-west1",
)

# Alternative: Use Gemini API with API key 
# client = genai.Client(api_key="YOUR_API_KEY_HERE")

print("=== Chat Conversation Example ===\n")

# Create a chat session
chat = client.chats.create(model="gemini-2.5-flash")

# First message
print("User: What is Python?")
response1 = chat.send_message("What is Python?")
print(f"AI: {response1.text}\n")

# Follow-up message (context is preserved from previous message)
print("User: What are its main uses?")
response2 = chat.send_message("What are its main uses?")
print(f"AI: {response2.text}\n")

# Another follow-up (AI remembers we're talking about Python)
print("User: Can you show me a simple example?")
response3 = chat.send_message("Can you show me a simple example?")
print(f"AI: {response3.text}\n")

print("Chat complete! ✨")
