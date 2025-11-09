"""
URL Grounding with Gemini
Let the AI fetch and analyze content from websites automatically
"""

from google import genai
from google.genai.types import Tool, GenerateContentConfig

# Initialize Genai client with Vertex AI authentication
# Make sure you've run: gcloud auth application-default login
client = genai.Client(
    vertexai=True,
    project="metro-markets-sms-dev",
    location="europe-west1",
)

# Alternative: Use Gemini API with API key 
# client = genai.Client(api_key="YOUR_API_KEY_HERE")

print("=" * 70)
print("URL Grounding Demo - AI Fetches Web Content Automatically")
print("=" * 70)
print()

# Define the URL context tool (allows AI to fetch web content)
tools = [
    {"url_context": {}},
]

# Example 1: Compare recipes from two websites
print("Example 1: Comparing Two Recipe Websites")
print("-" * 70)

url1 = "https://www.foodnetwork.com/recipes/ina-garten/perfect-roast-chicken-recipe-1940592"
url2 = "https://www.allrecipes.com/recipe/21151/simple-whole-roast-chicken/"

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Compare the ingredients and cooking times from the recipes at {url1} and {url2}",
    config=GenerateContentConfig(
        tools=tools,
    )
)

print("Question: Compare ingredients and cooking times from two recipe sites\n")
for each in response.candidates[0].content.parts:
    print(each.text)

# Show which URLs were actually fetched
print("\n📊 URLs Retrieved by AI:")
print(response.candidates[0].url_context_metadata)
print()

# Example 2: Analyze product documentation
print("\nExample 2: Analyzing Technical Documentation")
print("-" * 70)

doc_url = "https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini"

response2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"What are the key features of Gemini models mentioned at {doc_url}? List 5 main points.",
    config=GenerateContentConfig(
        tools=tools,
    )
)

print(f"Question: What are key features from Vertex AI documentation?\n")
for each in response2.candidates[0].content.parts:
    print(each.text)

print("\n📊 URLs Retrieved by AI:")
print(response2.candidates[0].url_context_metadata)
print()

# Example 3: Get current information
print("\nExample 3: Fetching Current Information")
print("-" * 70)

news_url = "https://cloud.google.com/blog/products/ai-machine-learning"

response3 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Summarize the latest AI/ML updates from {news_url}. What are the 3 most recent announcements?",
    config=GenerateContentConfig(
        tools=tools,
    )
)

print(f"Question: What are the latest AI/ML announcements?\n")
for each in response3.candidates[0].content.parts:
    print(each.text)

print("\n📊 URLs Retrieved by AI:")
print(response3.candidates[0].url_context_metadata)
print()

# Example 4: Extract product price from e-commerce site
print("\nExample 4: Extracting Product Price from E-commerce")
print("-" * 70)

product_url = "https://www.baur.de/p/AKLBB346296310?sku=3710210237&ref=reco&lmPromo=la,1,hk,detailview,fl,prudsysProducts_16_1_6150__37102102_product_OutputElement0"

response4 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"What is the price of the product at {product_url}? Also tell me the product name.",
    config=GenerateContentConfig(
        tools=tools,
    )
)

print(f"Question: What is the product price?\n")
for each in response4.candidates[0].content.parts:
    print(each.text)

print("\n📊 URLs Retrieved by AI:")
print(response4.candidates[0].url_context_metadata)

print("\n" + "=" * 70)
print("Tutorial complete! ✨")
print("\nKey Takeaway: With URL grounding, the AI can:")
print("  - Fetch content from any public URL")
print("  - Compare information across multiple sites")
print("  - Get real-time/current information")
print("  - Analyze documentation, articles, recipes, etc.")
print("  - Extract product prices and details from e-commerce sites")
print("=" * 70)
