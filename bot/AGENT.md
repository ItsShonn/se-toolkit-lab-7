# Bot Agent Architecture

## Overview

This is a Telegram bot agent for the Learning Management System (LMS). It provides students with a conversational interface to query lab scores, view available labs, and check backend health.

## Architecture

### Separation of Concerns

The bot follows a **testable handler architecture** with clear separation:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Transport      │ ──→ │  Handlers        │ ──→ │  Services       │
│  (Telegram/CLI) │     │  (Business Logic)│     │  (API Clients)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Components

#### 1. Entry Point (`bot.py`)

- Handles CLI `--test` mode for offline testing
- Routes commands to appropriate handlers
- Contains Telegram integration (when running in production)

#### 2. Handlers (`handlers/`)

Pure functions that take input and return responses:

| Handler | Command | Description |
|---------|---------|-------------|
| `handle_start` | `/start` | Welcome message |
| `handle_help` | `/help` | Lists available commands |
| `handle_health` | `/health` | Checks backend status |
| `handle_labs` | `/labs` | Lists available labs |
| `handle_scores` | `/scores <lab>` | Per-task pass rates |

#### 3. Services (`services/`)

API clients for external services:

- **`LMSClient`**: HTTP client for the LMS backend API
  - `health_check()` - Verify backend is running
  - `get_labs()` - Fetch available labs
  - `get_pass_rates(lab)` - Fetch per-task scores

- **`LLMClient`**: HTTP client for AI model (intent classification)

#### 4. Configuration (`config.py`)

Loads settings from `.env.bot.secret`:
- `BOT_TOKEN` - Telegram bot authentication
- `LMS_API_BASE_URL`, `LMS_API_KEY` - Backend API access
- `LLM_API_*` - AI model configuration

## Error Handling

All handlers implement graceful error handling:
- Backend errors show user-friendly messages with actual error details
- Missing arguments prompt users for correct usage
- No raw tracebacks exposed to users

## Testing

Run tests with:
```bash
# Unit tests
uv run pytest tests/ -v

# Test mode (no Telegram needed)
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"
```
