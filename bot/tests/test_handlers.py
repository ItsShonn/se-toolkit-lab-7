"""Tests for bot command handlers."""

import pytest

from bot.handlers.help import handle_help
from bot.handlers.health import handle_health
from bot.handlers.labs import handle_labs
from bot.handlers.scores import handle_scores
from bot.handlers.start import handle_start


class TestHandleStart:
    """Tests for the /start command handler."""

    def test_start_returns_welcome_message(self):
        """Test that /start returns a welcome message."""
        response = handle_start()
        assert "welcome" in response.lower() or "👋" in response

    def test_start_contains_bot_name(self):
        """Test that /start mentions the bot."""
        response = handle_start()
        assert "bot" in response.lower()

    def test_start_with_empty_input(self):
        """Test that /start works with empty input."""
        response = handle_start("")
        assert len(response) > 0

    def test_start_ignores_extra_input(self):
        """Test that /start ignores extra input."""
        response1 = handle_start()
        response2 = handle_start("some extra text")
        assert response1 == response2


class TestHandleHelp:
    """Tests for the /help command handler."""

    def test_help_lists_commands(self):
        """Test that /help lists available commands."""
        response = handle_help()
        assert "/start" in response
        assert "/help" in response

    def test_help_lists_at_least_four_commands(self):
        """Test that /help lists at least 4 commands."""
        response = handle_help()
        commands = [line for line in response.split("\n") if line.strip().startswith("/")]
        assert len(commands) >= 4

    def test_help_with_empty_input(self):
        """Test that /help works with empty input."""
        response = handle_help("")
        assert len(response) > 0


class TestHandleHealth:
    """Tests for the /health command handler."""

    def test_health_shows_bot_status(self):
        """Test that /health shows bot is running."""
        response = handle_health()
        assert "bot" in response.lower()

    def test_health_with_empty_input(self):
        """Test that /health works with empty input."""
        response = handle_health("")
        assert len(response) > 0


class TestHandleLabs:
    """Tests for the /labs command handler."""

    def test_labs_returns_text(self):
        """Test that /labs returns some text."""
        response = handle_labs()
        assert isinstance(response, str)
        assert len(response) > 0

    def test_labs_with_empty_input(self):
        """Test that /labs works with empty input."""
        response = handle_labs("")
        assert len(response) > 0


class TestHandleScores:
    """Tests for the /scores command handler."""

    def test_scores_without_lab_prompts_for_lab(self):
        """Test that /scores without lab name prompts user."""
        response = handle_scores()
        assert "specify a lab" in response.lower() or "/scores lab-" in response

    def test_scores_with_empty_string_prompts_for_lab(self):
        """Test that /scores with empty string prompts user."""
        response = handle_scores("")
        assert "specify a lab" in response.lower() or "/scores lab-" in response

    def test_scores_with_lab_name_returns_response(self):
        """Test that /scores with lab name returns a response."""
        response = handle_scores("lab-04")
        assert isinstance(response, str)
        assert len(response) > 0
