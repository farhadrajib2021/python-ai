# Long-Running Workflow with App + ResumabilityConfig

This example demonstrates the **programmatic pattern** for human-in-the-loop workflows using:
- `App` wrapper with `ResumabilityConfig`
- `ToolContext.request_confirmation()` in tool functions
- `Runner` with sessions for programmatic execution

## 🎯 When to Use This Pattern

Use this pattern for **programmatic workflows** where:
- You're building automation systems that need human approval at certain steps
- Your code controls when to pause and resume workflows
- You need to store workflow state and resume later
- You're integrating agent workflows into backend services or APIs

## ⚠️ Not for Interactive Chat

**This pattern does NOT work with `adk web`** - it's designed for programmatic control, not interactive chat interfaces.

For interactive chat (like `adk web`), use the **conversational pattern** in `../multi-agent-long-running/` folder.

## 🔑 Key Components

### 1. Tool with ToolContext

```python
def place_shipping_order_with_approval(
    num_containers: int, 
    destination: str, 
    tool_context: ToolContext
) -> dict:
    if num_containers > 5:
        if not tool_context.tool_confirmation:
            # First call - request approval
            tool_context.request_confirmation(
                hint=f"Large order: {num_containers} containers to {destination}",
                payload={"num_containers": num_containers, "destination": destination}
            )
            return {"status": "pending_approval"}
        
        # Second call - process confirmation
        if tool_context.tool_confirmation.confirmed:
            return {"status": "approved", "order_id": f"ORD-{num_containers}-HUMAN"}
        else:
            return {"status": "rejected"}
    
    # Small orders auto-approve
    return {"status": "approved", "order_id": f"ORD-{num_containers}-AUTO"}
```

### 2. App with ResumabilityConfig

```python
shipping_app = App(
    name="shipping_app",
    root_agent=shipping_agent,
    resumability_config=ResumabilityConfig()
)
```

### 3. Programmatic Workflow Execution

```python
session_service = InMemorySessionService()
runner = Runner(
    app_name="shipping_app",
    agent=shipping_agent,
    session_service=session_service
)

# Run workflow
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(parts=[types.Part(text="Ship 20 containers to Berlin")])
):
    # Process events
    ...
```

## 🚀 Running the Example

### Run Programmatically

```bash
python agent.py
```

This will run automated tests demonstrating:
1. Small order (3 containers) - auto-approved
2. Large order (20 containers) - requires approval (shows pending state)

### Try with ADK CLI (Limited Support)

```bash
adk run multi-agent-long-running-from-script --new-message "Ship 3 containers to Singapore"
```

**Note**: The confirmation mechanism works when the agent is called, but the ADK CLI doesn't have built-in support for providing programmatic confirmations via the command line.

## 📊 Comparison: Two Patterns for Human-in-the-Loop

| Aspect | Programmatic (This Folder) | Conversational (multi-agent-long-running) |
|--------|----------------------------|-------------------------------------------|
| **Pattern** | `ToolContext.request_confirmation()` | Two separate tools (place + approve) |
| **Agent Type** | `App` + `ResumabilityConfig` | Simple `LlmAgent` |
| **Interface** | Runner + sessions | `adk web` / `adk run` |
| **Use Case** | Backend automation, APIs | Interactive chat, web UI |
| **Approval** | Programmatic via confirmations param | Conversational via user message |
| **State** | Pauses workflow, resumable | Conversational flow |

## 🎓 Learning Points

1. **ToolContext** provides a way to request confirmations within tool execution
2. **ResumabilityConfig** enables workflows to pause and resume (experimental feature)
3. **App wrapper** is needed for advanced features like resumability
4. **Runner** provides programmatic control over agent execution
5. For **interactive chat**, use the simpler conversational pattern instead

## 🔗 Related Examples

- **Interactive Pattern**: See `../multi-agent-long-running/` for the conversational approval pattern that works with `adk web`
- **Sequential Agents**: See `../multi-agent-sequential/` for chaining agents
- **MCP Integration**: See `../multi-agent-mcp/` for database tool integration

## 📝 Notes

- `ResumabilityConfig` is marked as **experimental** in ADK and may change
- The confirmation mechanism requires proper session management
- For production use, consider using persistent session storage instead of `InMemorySessionService`
- The agent provides feedback about the approval status, but the actual resume logic would need to be implemented in your application code
