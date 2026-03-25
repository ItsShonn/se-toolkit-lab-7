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
    # Bot is running (we're here, so it is)
    bot_status = "✅ Bot: Running"

    # Check backend health
    try:
        lms_client = LMSClient()
        if not lms_client.base_url:
            return f"{bot_status}\n⚠️ LMS API: Not configured (LMS_API_BASE_URL not set)"

        status = lms_client.health_check()

        if status.healthy:
            return f"{bot_status}\n✅ Backend is healthy. {status.item_count} items available."
        else:
            error_msg = status.error or "Unknown error"
            return f"{bot_status}\n❌ Backend error: {error_msg}"

    except Exception as e:
        error_msg = str(e)
        # Make error message user-friendly but include actual error
        if "connection refused" in error_msg.lower():
            return f"{bot_status}\n❌ Backend error: connection refused ({LMSClient().base_url}). Check that the services are running."
        elif "http" in error_msg.lower():
            return f"{bot_status}\n❌ Backend error: {error_msg}"
        else:
            return f"{bot_status}\n❌ Backend error: {error_msg}"
