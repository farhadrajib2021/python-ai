from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search


# Custom tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    print(f"🔧 TOOL CALLED: get_current_time(city='{city}')")
    return {"status": "success", "city": city, "time": "10:30 AM"}

# Option 1: Use only google_search (recommended for web queries)
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="A helpful assistant that can search the web for information.",
    instruction="You are a helpful assistant. Search the web using 'google_search' when users need information about current events, facts, or anything requiring up-to-date data.",
    tools=[google_search],
)

# Option 2: Use only custom functions (uncomment to use)
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description="A helpful assistant that can tell the current time.",
#     instruction="You are a helpful assistant. Tell the current time in cities using 'get_current_time'.",
#     tools=[get_current_time],
# )
