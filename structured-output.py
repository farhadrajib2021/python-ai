"""
Structured Output with JSON Schema
Extracting multipack product information from product names in multiple languages
"""

import json
import yaml
from google import genai
from google.genai import types

# Initialize Genai client with Vertex AI authentication
# Make sure you've run: gcloud auth application-default login
client = genai.Client(
    vertexai=True,
    project="metro-markets-sms-dev",
    location="europe-west1",
)

# Alternative: Use Gemini API with API key 
# client = genai.Client(api_key="YOUR_API_KEY_HERE")

# Define the response schema for multipack extraction
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "valid": {
            "type": "boolean",
            "description": "Indicates whether all product names describe the same pack configuration. If false, no other properties may be present."
        },
        "quantity": {
            "type": "object",
            "description": "Total number of items in the retail unit (e.g., 5 packages x 20 items ⇒ 100). Present only when valid=true.",
            "properties": {
                "value": {
                    "type": "integer",
                    "description": "Total number of items in the retail unit."
                },
                "confidence_rate": {
                    "type": "number",
                    "description": "Confidence in [0,1]."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of how the value was determined."
                }
            },
            "required": ["value"]
        },
        "count_of_pieces_per_package": {
            "type": "object",
            "description": "Items per package (if applicable; else 1). Present only when valid=true.",
            "properties": {
                "value": {
                    "type": "integer"
                },
                "confidence_rate": {
                    "type": "number",
                    "description": "Confidence in [0,1]."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of how the value was determined."
                }
            },
            "required": ["value"]
        },
        "count_of_packages": {
            "type": "object",
            "description": "Number of packages in the retail unit (default 1 if not explicitly a multipack). Present only when valid=true.",
            "properties": {
                "value": {
                    "type": "integer"
                },
                "confidence_rate": {
                    "type": "number",
                    "description": "Confidence in [0,1]."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of how the value was determined."
                }
            },
            "required": ["value"]
        }
    },
    "required": ["valid"]
}

# System instructions for the AI
SYSTEM_ROLE = """
You are a data extraction assistant specializing in product information **from product names only** across multiple locales.
Your task is to extract multipack attributes **only if all provided product names describe the same pack configuration**.

Critical rules:
1) If any name implies a different pack configuration (different items per package, different number of packages, or different total quantity), output **only**:
   {"valid": false}
   - Do **not** include `quantity`, `count_of_pieces_per_package`, or `count_of_packages` in that case.
2) When all names are consistent, set `valid=true` and extract:
   - quantity: total number of items in the retail unit. (Example: 5 packages × 20 items ⇒ 100)
   - count_of_pieces_per_package: number of items in each package (if applicable; else 1).
   - count_of_packages: number of packages in the retail unit (if not explicit, default to 1).
3) Prefer information found directly in the product **name**. Ignore other attributes not present in the names.
4) Volume markers like "4cl" or "47cl" indicate per-item capacity, not pack size; use them only to check alignment across names.
5) Ensure Quantity = count_of_packages × count_of_pieces_per_package when valid=true.
"""

# Sample product data (hardcoded with multiple language variants)
sample_product = {
    'MID': '123456',
    'GTIN': '03011248060326',
    'Product Name DE': "Arcoroc Versatile Dessertschalen aus Glas 4cl",
    'Product Name ES': "Arcoroc Versatile - Set 12 Copas Helado Vidrio 4Cl",
    'Product Name NL': "Coppa Dessert Versatile Cl 4 H 6 √ò Cm 6,7 Arcoroc Set Da 48",
    'Brand': 'Arcoroc',
}

# Convert product data to YAML format for better readability
product_yaml = yaml.dump(sample_product, allow_unicode=True, default_flow_style=False)

# Create the prompt
prompt = f"""Generate a JSON response for the following product data:
{product_yaml}

The response should be in JSON which fits to this schema:
{json.dumps(RESPONSE_SCHEMA, indent=2)}"""

# Generate response with structured output
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=RESPONSE_SCHEMA,
        system_instruction=SYSTEM_ROLE
    )
)

# Parse and display the JSON response
result = json.loads(response.text)

print("Multipack Product Analysis:")
print("=" * 60)
print(json.dumps(result, indent=2, ensure_ascii=False))
print("=" * 60)

# Display results in a readable format
if result.get("valid"):
    print("\n✅ Valid multipack product (all names consistent)")
    print(f"\nTotal Quantity: {result['quantity']['value']}")
    print(f"  Confidence: {result['quantity'].get('confidence_rate', 'N/A')}")
    print(f"  Reasoning: {result['quantity'].get('reasoning', 'N/A')}")
    
    print(f"\nPieces per Package: {result['count_of_pieces_per_package']['value']}")
    print(f"  Confidence: {result['count_of_pieces_per_package'].get('confidence_rate', 'N/A')}")
    print(f"  Reasoning: {result['count_of_pieces_per_package'].get('reasoning', 'N/A')}")
    
    print(f"\nNumber of Packages: {result['count_of_packages']['value']}")
    print(f"  Confidence: {result['count_of_packages'].get('confidence_rate', 'N/A')}")
    print(f"  Reasoning: {result['count_of_packages'].get('reasoning', 'N/A')}")
else:
    print("\n❌ Invalid: Product names describe different pack configurations")
