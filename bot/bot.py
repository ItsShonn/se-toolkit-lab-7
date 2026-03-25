#!/usr/bin/env python3
"""Telegram bot entry point with test mode support.

Usage:
    # Test mode (no Telegram connection needed)
    uv run bot.py --test "/start"
    uv run bot.py --test "/help"
    uv run bot.py --test "what labs are available"

    # Production mode (connects to Telegram)
    uv run bot.py
"""

import argparse
import sys
from pathlib import Path

# Ensure the bot directory is in the Python path
bot_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(bot_dir.parent))

from bot.handlers import handle_help, handle_health, handle_labs, handle_scores, handle_start
from bot.services.llm_client import LLMClient


# Command routing map
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

    # Check if it starts with a command
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return command, args

    # Natural language - will be handled by intent classifier
    return "", text


def handle_message(text: str) -> str:
    """Handle a user message and return a response.

    Args:
        text: User input text

    Returns:
        Response text
    """
    command, args = parse_command(text)

    # Check for direct command match
    if command in COMMAND_HANDLERS:
        handler = COMMAND_HANDLERS[command]
        return handler(args)

    # Natural language query - use intent classification
    if text:
        llm = LLMClient()
        intent = llm.classify_intent(text)

        # Route based on intent
        if intent == "check_scores":
            return handle_scores(args or text)
        if intent == "list_labs":
            return handle_labs(text)
        if intent == "get_help":
            return handle_help(text)
        if intent == "health_check":
            return handle_health(text)

    return "I didn't understand that command. Use /help to see available commands."


def run_test_mode(command: str) -> None:
    """Run the bot in test mode.

    Args:
        command: Command or message to test
    """
    response = handle_message(command)
    print(response)
    sys.exit(0)


def run_telegram_mode() -> None:
    """Run the bot with Telegram connection.

    This will be implemented in Task 2 when we add the actual
    Telegram bot integration.
    """
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart
    except ImportError:
        print(
            "Error: aiogram not installed. Run: uv add aiogram\n"
            "Or use --test mode for offline testing."
        )
        sys.exit(1)

    from config import settings

    if not settings.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        """Handle /start command from Telegram."""
        response = handle_start("")
        await message.answer(response)

    @dp.message()
    async def echo_handler(message: types.Message):
        """Handle all other messages."""
        response = handle_message(message.text or "")
        await message.answer(response)

    print(f"Bot starting... (token: {settings.bot_token[:10]}...)")
    dp.run_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Learning Management System Telegram Bot"
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command (no Telegram connection)",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
