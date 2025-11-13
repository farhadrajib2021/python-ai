import os
from google.genai import types
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Configure MCP Toolset for SQLite using GenAI Toolbox
# This uses the toolbox.yaml configuration file
# The toolbox binary must be in the same directory or in PATH
agent_dir = os.path.dirname(os.path.abspath(__file__))
toolbox_path = os.path.join(agent_dir, "toolbox")
toolbox_config = os.path.join(agent_dir, "toolbox.yaml")

mysql_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=toolbox_path,  # GenAI Toolbox CLI
            args=[
                "--stdio",
                "--tools-file", toolbox_config,  # Config file path with absolute path
            ],
            cwd=agent_dir,  # Set working directory
        ),
        timeout=30,
    )
)

# Create database agent with MCP integration
root_agent = Agent(
    model='gemini-2.5-flash',
    name='database_agent',
    description='A database agent that can query the local SQLite test database via MCP.',
    instruction="""You are a helpful database assistant for the test products database.

    You have access to SQLite database tools via MCP.
    
    When a user asks about data:
    1. List available tables to see the database structure
    2. Construct appropriate SQL queries
    3. Execute queries to retrieve data
    4. Present results in a clear, formatted way
    
    The database contains a 'products' table with: id, name, category, price, stock
    
    Always be cautious with queries and explain what you're doing.
    Focus on SELECT queries for data retrieval.
    """,
    tools=[mysql_mcp_toolset],
)

print("✅ Database agent created with MCP SQLite integration")
print("📊 Connected to: test_database.db (local SQLite)")
print("🔧 MCP Tools available via GenAI Toolbox")
