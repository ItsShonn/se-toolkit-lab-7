#!/usr/bin/env python3
"""CLI entry point for the LMS bot agent.

Usage:
    python agent.py "What labs are available?"
    python agent.py "/health"
    python agent.py "/scores lab-04"

Returns JSON response with the bot's answer.
"""

import json
import sys
from pathlib import Path

# Ensure the parent directory is in the Python path
bot_dir = Path(__file__).resolve().parent
parent_dir = bot_dir.parent
sys.path.insert(0, str(parent_dir))

from bot.handlers import handle_help, handle_health, handle_labs, handle_scores, handle_start
from bot.services.llm_client import LLMClient


COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command from user input.

    Args:
        text: User input text

    Returns:
        Tuple of (command, arguments)
    """
    text = text.strip()

    if not text:
        return "", ""

    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return command, args

    return "", text


def handle_message(text: str) -> str:
    """Handle a user message and return a response.

    Args:
        text: User input text

    Returns:
        Response text
    """
    command, args = parse_command(text)

    if command in COMMAND_HANDLERS:
        handler = COMMAND_HANDLERS[command]
        return handler(args)

    if text:
        llm = LLMClient()
        intent = llm.classify_intent(text)

        if intent == "check_scores":
            return handle_scores(args or text)
        if intent == "list_labs":
            return handle_labs(text)
        if intent == "get_help":
            return handle_help(text)
        if intent == "health_check":
            return handle_health(text)

    return "I didn't understand that command. Use /help to see available commands."


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No question provided",
            "usage": "python agent.py <question>"
        }))
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    response = handle_message(question)

    print(json.dumps({
        "question": question,
        "response": response
    }))


if __name__ == "__main__":
    main()
