"""
Simple Text Generation with Gemini
The most basic example - just prompt and response
"""

from google import genai

# Initialize Genai client with Vertex AI authentication (recommended for GCP)
# Make sure you've run: gcloud auth application-default login
client = genai.Client(
    vertexai=True,
    project="metro-markets-sms-dev",
    location="europe-west1",
)

# Alternative: Use Gemini API with API key 
# client = genai.Client(api_key="YOUR_API_KEY_HERE")

# Create a simple prompt
prompt = "What is the capital of Germany?"

# Generate response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

# Print the result
print(f"Prompt: {prompt}")
print(f"Response: {response.text}")
