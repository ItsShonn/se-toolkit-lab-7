"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return responses.
They have no knowledge of Telegram - this enables testable, offline verification.
"""

from bot.handlers.start import handle_start
from bot.handlers.help import handle_help
from bot.handlers.health import handle_health
from bot.handlers.labs import handle_labs
from bot.handlers.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
