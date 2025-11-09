"""
Function Calling (Tools) with Gemini
AI automatically calls your Python functions when needed
"""

from google import genai
from google.genai import types
from google.cloud import logging
from datetime import datetime, timedelta
import json

# Initialize Genai client with Vertex AI authentication
# Make sure you've run: gcloud auth application-default login
client = genai.Client(
    vertexai=True,
    project="metro-markets-sms-dev",
    location="europe-west1",
)

# Alternative: Use Gemini API with API key 
# client = genai.Client(api_key="YOUR_API_KEY_HERE")

# Configuration
PROJECT_ID = "metro-markets-sms-prod"

# --- Define Your Python Functions ---

def fetch_cloud_logs(country: str, gtin: str = None, days_back: int = 7) -> str:
    """
    Fetch logs from Google Cloud Logging
    This is the actual function that will be called by the AI
    """
    print(f"--- Function called: fetch_cloud_logs(country='{country}', gtin='{gtin}', days_back={days_back}) ---")
    
    # Build the filter
    one_week_ago = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    filter_str = f'''resource.type="k8s_container"
resource.labels.project_id="metro-markets-sms-prod"
resource.labels.location="europe-west1"
resource.labels.cluster_name="sms-25b58e2d-gke"
resource.labels.namespace_name="prod"
labels.k8s-pod/app_kubernetes_io/instance="price-crawling"
labels.k8s-pod/app_kubernetes_io/name="price-crawling-consumer-ac-store-price-v2"
jsonPayload.context.message.country="{country}"'''
    
    if gtin:
        filter_str += f'\njsonPayload.context.message.identifiers.value="{gtin}"'
    
    filter_str += f'\ntimestamp>="{one_week_ago}"'
    
    try:
        # Fetch logs
        logging_client = logging.Client(project=PROJECT_ID)
        entries = list(logging_client.list_entries(
            filter_=filter_str,
            page_size=5,
            order_by=logging.DESCENDING
        ))
        
        if not entries:
            return f"No logs found for country={country}, gtin={gtin}"
        
        # Format results
        result = {
            "count": len(entries),
            "logs": []
        }
        
        for entry in entries:
            result["logs"].append({
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else "N/A",
                "severity": entry.severity,
                "payload_summary": str(entry.payload)[:200] + "..." if len(str(entry.payload)) > 200 else str(entry.payload)
            })
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Error fetching logs: {str(e)}"


# --- Declare the Function to Gemini ---

fetch_logs_declaration = types.FunctionDeclaration(
    name="fetch_cloud_logs",
    description="Fetches logs from Google Cloud Logging for a specific country and optional GTIN. Use this when user asks about logs, store data, or is_sellable status.",
    parameters={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Country code (e.g., DE, ES, PT, NL)"
            },
            "gtin": {
                "type": "string",
                "description": "Product GTIN/identifier (optional)"
            },
            "days_back": {
                "type": "integer",
                "description": "Number of days to look back (default: 7)"
            }
        },
        "required": ["country"]
    }
)

# Create a Tool with the function
logs_tool = types.Tool(
    function_declarations=[fetch_logs_declaration]
)

print("=" * 70)
print("Function Calling Demo - Cloud Logs Analysis")
print("=" * 70)
print("\nThe AI can automatically call fetch_cloud_logs() when needed!")
print("\nTry asking:")
print("  - 'Show me logs for Germany'")
print("  - 'Get logs for DE with GTIN 8004360075199'")
print("  - 'What is function calling?' (won't trigger function)")
print("\nType 'exit' to quit\n")

# Interactive loop
while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    
    # Send message to AI with tools enabled
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_input,
        config=types.GenerateContentConfig(
            tools=[logs_tool]
        )
    )
    
    # Check if AI wants to call a function
    function_call = response.candidates[0].content.parts[0].function_call
    
    if function_call and function_call.name:
        print(f"\n🤖 AI decided to call function: {function_call.name}")
        
        # Extract arguments
        args = dict(function_call.args)
        country = args.get("country")
        gtin = args.get("gtin")
        days_back = args.get("days_back", 7)
        
        # Execute the actual Python function
        function_result = fetch_cloud_logs(country=country, gtin=gtin, days_back=days_back)
        
        # Send the function result back to the AI
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_input)]
                ),
                types.Content(
                    role="model",
                    parts=[types.Part(function_call=function_call)]
                ),
                types.Content(
                    role="function",
                    parts=[types.Part(
                        function_response=types.FunctionResponse(
                            name=function_call.name,
                            response={"content": function_result}
                        )
                    )]
                )
            ],
            config=types.GenerateContentConfig(
                tools=[logs_tool]
            )
        )
        
        print(f"\n✨ AI Response (after using function):\n{response.text}\n")
    else:
        # AI responded directly without calling a function
        print(f"\n✨ AI Response (direct answer):\n{response.text}\n")
