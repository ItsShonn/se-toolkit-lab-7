"""Handler for /start command."""


def handle_start(user_input: str = "") -> str:
    """Handle the /start command.

    Args:
        user_input: Optional additional input from user (ignored for /start)

    Returns:
        Welcome message text
    """
    return (
        "👋 Welcome to the Learning Management System Bot!\n\n"
        "I can help you with:\n"
        "• Check your lab scores\n"
        "• View available labs\n"
        "• Submit your solutions\n"
        "• Get AI-powered assistance\n\n"
        "Use /help to see all available commands."
    )
