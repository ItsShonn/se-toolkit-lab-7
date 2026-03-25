"""Handler for /scores command."""

from bot.services.lms_client import LMSClient


def handle_scores(user_input: str = "") -> str:
    """Handle the /scores command.

    Shows the user's scores for a specific lab or all labs.

    Args:
        user_input: Optional lab name (e.g., "lab-04")

    Returns:
        Score information
    """
    if not user_input or not user_input.strip():
        return (
            "📊 Your Scores:\n\n"
            "Please specify a lab to view scores:\n"
            "/scores lab-01\n"
            "/scores lab-04\n\n"
            "Use /labs to see all available labs."
        )

    lab_name = user_input.strip()

    try:
        lms_client = LMSClient()
        if not lms_client.base_url:
            return (
                f"📊 Scores for {lab_name}:\n\n"
                "⚠️ LMS API is not configured.\n"
                "Please set LMS_API_BASE_URL and LMS_API_KEY in your environment."
            )

        scores = lms_client.get_pass_rates(lab_name)

        if not scores:
            # Try to get a nicer lab title for the error message
            lab_display = lab_name.replace("lab-", "Lab ").replace("-", " ").title()
            return (
                f"📊 Pass rates for {lab_display}:\n\n"
                f"No data available for lab '{lab_name}'.\n"
                f"The lab may not exist or has no submissions yet.\n\n"
                "Use /labs to see all available labs."
            )

        # Format lab name for display
        lab_display = lab_name.replace("lab-", "Lab ").lstrip("0")
        if lab_display[3:].isdigit():
            # Convert "Lab 4" to "Lab 04" format for consistency
            num = lab_display[4:]
            lab_display = f"Lab {num.zfill(2)}"

        # Format scores
        score_lines = []
        for score in scores:
            percentage = f"{score.avg_score:.1f}%"
            attempts = f"({score.attempts} attempts)"
            score_lines.append(f"- {score.task}: {percentage} {attempts}")

        return f"📊 Pass rates for {lab_display}:\n" + "\n".join(score_lines)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            lab_display = lab_name.replace("lab-", "Lab ").lstrip("0")
            return (
                f"📊 Pass rates for {lab_display}:\n\n"
                f"Lab '{lab_name}' not found.\n\n"
                "Use /labs to see all available labs."
            )
        return f"❌ Error: {error_msg}"

    except RuntimeError as e:
        error_msg = str(e)
        return f"❌ Error fetching scores: {error_msg}"

    except Exception as e:
        error_msg = str(e)
        # Make error message user-friendly but include actual error
        if "connection refused" in error_msg.lower():
            return f"❌ Backend error: connection refused. Check that the services are running."
        else:
            return f"❌ Error fetching scores: {error_msg}"
