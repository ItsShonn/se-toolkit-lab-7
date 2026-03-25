# Task 1: Call an LLM from Code - Implementation Plan

## Objective

Create a bot that can call an LLM API to classify user intents and route commands appropriately.

## Requirements

1. **LLM Client** - HTTP client to call LLM API
2. **Intent Classification** - Classify user messages into intents
3. **Command Routing** - Route to appropriate handlers based on intent
4. **Fallback** - Keyword-based classification if LLM is unavailable

## Implementation Steps

### Step 1: Create LLM Client (`services/llm_client.py`)

```python
class LLMClient:
    - Initialize with API key and base URL
    - classify_intent(user_message) -> intent string
    - generate_response(context, question) -> response text
```

### Step 2: Intent Classification

Map user messages to intents:
- `check_scores` - "show my scores", "lab-04 results"
- `list_labs` - "what labs", "available assignments"
- `get_help` - "help", "commands"
- `health_check` - "status", "is backend working"
- `submit_solution` - "submit", "upload"
- `other` - unrecognized

### Step 3: Update Bot Entry Point

- Parse commands from user input
- Use LLM to classify natural language
- Route to appropriate handler

### Step 4: Error Handling

- Graceful fallback to keyword matching
- User-friendly error messages
- No raw tracebacks

## Testing

```bash
# Test mode
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"

# Unit tests
uv run pytest tests/ -v
```

## Files Created

- `services/llm_client.py` - LLM API client
- `tests/test_llm_client.py` - LLM client tests
- `plans/task-1.md` - This plan
