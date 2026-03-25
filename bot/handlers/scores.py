"""Handler for /scores command."""


def handle_scores(user_input: str = "") -> str:
    """Handle the /scores command.

    Shows the user's scores for a specific lab or all labs.

    Args:
        user_input: Optional lab name (e.g., "lab-04")

    Returns:
        Score information
    """
    if user_input:
        # User requested specific lab
        lab_name = user_input.strip()
        return (
            f"📊 Scores for {lab_name}:\n\n"
            f"Status: Placeholder - API integration coming in Task 2\n"
            f"Your score: Will be fetched from LMS API\n\n"
            f"Use /help for more commands."
        )

    return (
        "📊 Your Scores:\n\n"
        "Please specify a lab to view scores:\n"
        "/scores lab-01\n"
        "/scores lab-04\n\n"
        "Or use /labs to see all available labs."
    )
