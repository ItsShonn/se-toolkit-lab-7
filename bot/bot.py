#!/usr/bin/env python3
"""Telegram bot entry point with test mode and LLM-powered intent routing.

Usage:
    # Test mode (no Telegram connection needed)
    uv run bot.py --test "/start"
    uv run bot.py --test "/help"
    uv run bot.py --test "what labs are available"
    uv run bot.py --test "which lab has the lowest pass rate"

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
from bot.services.intent_router import route_message


# Command routing map for direct commands
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

    # Natural language - will be handled by intent router
    return "", text


def handle_message(text: str, debug: bool = False) -> str:
    """Handle a user message and return a response.

    Args:
        text: User input text
        debug: If True, enable debug output

    Returns:
        Response text
    """
    command, args = parse_command(text)

    # Check for direct command match
    if command in COMMAND_HANDLERS:
        handler = COMMAND_HANDLERS[command]
        return handler(args)

    # Natural language query - use intent routing with LLM
    if text:
        return route_message(text, debug=debug)

    return "I didn't understand that command. Use /help to see available commands."


def run_test_mode(command: str, debug: bool = False) -> None:
    """Run the bot in test mode.

    Args:
        command: Command or message to test
        debug: If True, enable debug output
    """
    response = handle_message(command, debug=debug)
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
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    except ImportError:
        print(
            "Error: aiogram not installed. Run: uv add aiogram\n"
            "Or use --test mode for offline testing."
        )
        sys.exit(1)

    from bot.config import settings

    if not settings.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Inline keyboard for quick actions
    def get_main_keyboard() -> InlineKeyboardMarkup:
        """Get the main inline keyboard."""
        keyboard = [
            [
                InlineKeyboardButton(text="📋 Labs", callback_data="labs"),
                InlineKeyboardButton(text="📊 Scores", callback_data="scores"),
            ],
            [
                InlineKeyboardButton(text="💚 Health", callback_data="health"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        """Handle /start command from Telegram."""
        response = handle_start("")
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message()
    async def echo_handler(message: types.Message):
        """Handle all other messages."""
        response = handle_message(message.text or "")
        await message.answer(response)

    @dp.callback_query()
    async def callback_handler(callback: types.CallbackQuery):
        """Handle inline keyboard callbacks."""
        action = callback.data
        if action == "labs":
            response = handle_labs("")
        elif action == "scores":
            response = "Please specify a lab: /scores lab-04"
        elif action == "health":
            response = handle_health("")
        elif action == "help":
            response = handle_help("")
        else:
            response = "Unknown action"

        await callback.message.answer(response)
        await callback.answer()

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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output (shows tool calls to stderr)",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test, debug=args.debug)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
