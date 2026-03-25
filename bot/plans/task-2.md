# Task 2: The Documentation Agent - Implementation Plan

## Objective

Create a documentation agent that can read files and list directory contents using function calling with an LLM. The agent helps users explore and understand codebases by providing file system navigation capabilities.

## Requirements

1. **Tool Implementation**
   - `read_file(path)` - Read contents of a file
   - `list_files(path)` - List files in a directory

2. **Function Calling**
   - Define tool schemas for the LLM
   - LLM decides which tool to call based on user query
   - Execute tool and return results

3. **CLI Interface**
   - Accept natural language queries
   - Return JSON responses

## Implementation Steps

### Step 1: Define Tool Schemas

Create JSON schemas that describe the tools to the LLM:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory"}
                },
                "required": ["path"]
            }
        }
    }
]
```

### Step 2: Implement Tool Functions

```python
def read_file(path: str) -> str:
    """Read file contents."""
    # Implementation with error handling
    
def list_files(path: str) -> list[str]:
    """List directory contents."""
    # Implementation with error handling
```

### Step 3: LLM Integration

- Send user query with tool schemas to LLM
- Parse tool call response
- Execute the requested tool
- Return results to user

### Step 4: Error Handling

- File not found errors
- Permission errors
- Invalid paths

## Files to Create/Modify

- `plans/task-2.md` - This plan
- `agent.py` - Add read_file and list_files tools
- `tests/test_agent_tools.py` - Tests for new tools

## Testing

```bash
# Test read_file tool
uv run python agent.py "Read the file bot.py"

# Test list_files tool  
uv run python agent.py "List files in the current directory"

# Run unit tests
uv run pytest tests/test_agent_tools.py -v
```

## Success Criteria

1. Agent can read file contents when asked
2. Agent can list directory contents when asked
3. LLM correctly chooses between tools based on query
4. All tests pass
