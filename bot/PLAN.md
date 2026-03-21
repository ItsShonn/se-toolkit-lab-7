# Bot Development Plan

## Overview

This document outlines the development plan for the Learning Management System (LMS) Telegram bot. The bot provides students with a conversational interface to interact with the autochecker system, query their scores, submit solutions, and receive AI-powered assistance.

## Architecture

### Testable Handler Architecture (P0.1)

The core design principle is **separation of concerns**: command handlers are pure functions that take input and return responses. They have no knowledge of Telegram's API. This allows:

- **Offline testing** via `--test` mode without Telegram connection
- **Unit testing** handlers in isolation
- **Easy mocking** of external dependencies (LMS API, LLM API)
- **Transport agnosticism** - same handlers could work with Discord, Slack, or a web interface

The architecture follows this flow:

```
Telegram Message → bot.py (Telegram layer) → handlers/ (business logic) → services/ (API calls) → Response
                                                                                ↓
Test Mode: CLI args → bot.py (--test mode) → handlers/ (same functions) → services/ → stdout
```

### Handler Organization

Handlers are organized by command type:

- **System commands**: `/start`, `/help`, `/health` - basic bot functionality
- **LMS commands**: `/labs`, `/scores`, `/submissions` - interact with the autochecker API
- **Intent-based queries**: Natural language questions routed to appropriate handlers via LLM

### Services Layer

The `services/` directory contains API clients:

- **LMS Client**: HTTP client for the backend API (scores, submissions, labs)
- **LLM Client**: HTTP client for the AI model (intent classification, code review)

Both clients are designed with retry logic, timeout handling, and graceful degradation.

## Development Phases

### Phase 1: Scaffold (Task 1)

Create the project structure, entry point with `--test` mode, and placeholder handlers. Verify the architecture works by testing commands offline.

### Phase 2: Backend Integration (Task 2)

Implement real handlers that call the LMS backend API. Add proper error handling, caching, and response formatting.

### Phase 3: Intent Routing (Task 3)

Add LLM-powered intent classification. Natural language queries like "what labs are available" get routed to the appropriate handler.

### Phase 4: Deployment & Monitoring

Set up proper logging, health checks, and graceful restart handling. Deploy to production with monitoring.

## Configuration

The bot uses environment variables loaded from `.env.bot.secret`:

- `BOT_TOKEN`: Telegram bot authentication
- `LMS_API_BASE_URL`, `LMS_API_KEY`: Backend API access
- `LLM_API_KEY`, `LLM_API_BASE_URL`: AI model access

Test mode does not require `BOT_TOKEN` since it bypasses Telegram entirely.

## Testing Strategy

1. **Unit tests**: Test handlers with mocked services
2. **Integration tests**: Test full flow with test Telegram bot
3. **Manual testing**: Use `--test` mode for quick iteration
4. **Production monitoring**: Log all interactions for debugging

## Success Criteria

- All commands work in `--test` mode (exit code 0, non-empty output)
- Bot responds in Telegram within 5 seconds
- Graceful handling of API failures (inform user, don't crash)
- No sensitive data in logs
