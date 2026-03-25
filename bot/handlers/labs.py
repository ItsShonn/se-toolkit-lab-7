"""Handler for /labs command."""

from bot.services.lms_client import LMSClient


def handle_labs(user_input: str = "") -> str:
    """Handle the /labs command.

    Lists available labs and tasks.

    Args:
        user_input: Optional additional input (e.g., specific lab filter)

    Returns:
        List of available labs
    """
    try:
        lms_client = LMSClient()
        if not lms_client.base_url:
            return (
                "📋 Available Labs:\n\n"
                "⚠️ LMS API is not configured.\n"
                "Please set LMS_API_BASE_URL and LMS_API_KEY in your environment."
            )

        labs = lms_client.get_labs()

        if not labs:
            return "📋 No labs available at the moment."

        # Format lab list
        lab_lines = []
        for lab in labs:
            # Extract lab number from title like "Lab 01 — Products, Architecture & Roles"
            title = lab.title
            lab_lines.append(f"- {title}")

        return "📋 Available labs:\n" + "\n".join(lab_lines)

    except RuntimeError as e:
        error_msg = str(e)
        return f"❌ Error fetching labs: {error_msg}"
    except Exception as e:
        error_msg = str(e)
        # Make error message user-friendly but include actual error
        if "connection refused" in error_msg.lower():
            return f"❌ Backend error: connection refused. Check that the services are running."
        else:
            return f"❌ Error fetching labs: {error_msg}"
