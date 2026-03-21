"""Handler for /health command."""

from bot.services.lms_client import LMSClient


def handle_health(user_input: str = "") -> str:
    """Handle the /health command.

    Checks the health of the bot and backend services.

    Args:
        user_input: Optional additional input from user (ignored for /health)

    Returns:
        Health status message
    """
    status_parts = []

    # Bot is running (we're here, so it is)
    status_parts.append("✅ Bot: Running")

    # Check backend health
    try:
        lms_client = LMSClient()
        # For now, just report configured status
        if lms_client.base_url:
            status_parts.append(f"✅ LMS API: Configured ({lms_client.base_url})")
        else:
            status_parts.append("⚠️ LMS API: Not configured")
    except Exception as e:
        status_parts.append(f"❌ LMS API: Error - {str(e)}")

    return "\n".join(status_parts)
