"""Handler for /help command."""


def handle_help(user_input: str = "") -> str:
    """Handle the /help command.

    Args:
        user_input: Optional additional input from user (ignored for /help)

    Returns:
        List of available commands
    """
    return (
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check bot and backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View your scores for a lab\n\n"
        "You can also ask questions in natural language:\n"
        "• 'What labs are available?'\n"
        "• 'Show my score for lab-01'\n"
        "• 'How do I submit my solution?'"
    )
