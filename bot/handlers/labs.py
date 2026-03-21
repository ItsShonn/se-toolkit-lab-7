"""Handler for /labs command."""


def handle_labs(user_input: str = "") -> str:
    """Handle the /labs command.

    Lists available labs and tasks.

    Args:
        user_input: Optional additional input (e.g., specific lab filter)

    Returns:
        List of available labs
    """
    # Placeholder - will be implemented with LMS API integration in Task 2
    return (
        "📋 Available Labs:\n\n"
        "Lab 01: Introduction to Python\n"
        "Lab 02: Data Structures\n"
        "Lab 03: Algorithms\n"
        "Lab 04: Web Development Basics\n"
        "Lab 05: Database Design\n"
        "Lab 06: API Development\n"
        "Lab 07: Learning Management System\n\n"
        "Use /scores <lab-name> to view your scores for a specific lab.\n"
        "Example: /scores lab-04"
    )
