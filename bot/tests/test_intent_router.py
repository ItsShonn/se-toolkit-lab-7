"""Tests for the intent router with LLM tool calling."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
bot_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(bot_dir))

from bot.services.intent_router import IntentRouter, TOOL_DEFINITIONS, route_message


class TestToolDefinitions:
    """Tests for tool schema definitions."""

    def test_nine_tools_defined(self):
        """Test that all 9 tools are defined."""
        assert len(TOOL_DEFINITIONS) == 9

    def test_get_items_tool_exists(self):
        """Test that get_items tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        assert "get_items" in tool_names

    def test_get_pass_rates_tool_exists(self):
        """Test that get_pass_rates tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        assert "get_pass_rates" in tool_names

    def test_get_top_learners_tool_exists(self):
        """Test that get_top_learners tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        assert "get_top_learners" in tool_names

    def test_get_completion_rate_tool_exists(self):
        """Test that get_completion_rate tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        assert "get_completion_rate" in tool_names

    def test_trigger_sync_tool_exists(self):
        """Test that trigger_sync tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        assert "trigger_sync" in tool_names


class TestIntentRouter:
    """Tests for the IntentRouter class."""

    def test_router_initializes(self):
        """Test that IntentRouter can be initialized."""
        router = IntentRouter()
        assert router is not None

    def test_router_has_lms_client(self):
        """Test that router has LMS client."""
        router = IntentRouter()
        assert router.lms is not None

    def test_router_has_llm_client(self):
        """Test that router has LLM client."""
        router = IntentRouter()
        assert router.llm is not None


class TestRouteMessage:
    """Tests for the route_message function."""

    def test_route_message_returns_string(self):
        """Test that route_message returns a string."""
        result = route_message("hello")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_route_gibberish_returns_fallback(self):
        """Test that gibberish returns a helpful fallback message."""
        result = route_message("asdfgh")
        assert isinstance(result, str)
        # Should contain helpful suggestions
        assert "/labs" in result or "help" in result.lower()

    def test_route_short_message_returns_fallback(self):
        """Test that very short messages return fallback."""
        result = route_message("ab")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_route_greeting_returns_welcome(self):
        """Test that greetings return a welcome message."""
        result = route_message("hello")
        assert isinstance(result, str)
        assert "hello" in result.lower() or "help" in result.lower()


class TestExecuteTool:
    """Tests for tool execution."""

    def test_execute_unknown_tool_returns_error(self):
        """Test that unknown tool returns error."""
        router = IntentRouter()
        result = router._execute_tool("unknown_tool", {})
        assert result["error"] is not None
        assert "Unknown tool" in result.get("error", "")

    def test_execute_get_items_returns_data(self):
        """Test that get_items returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_items", {})
        assert isinstance(result, list)
        assert len(result) > 0

    def test_execute_get_learners_returns_data(self):
        """Test that get_learners returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_learners", {})
        assert isinstance(result, list)

    def test_execute_get_pass_rates_returns_data(self):
        """Test that get_pass_rates returns data for valid lab."""
        router = IntentRouter()
        result = router._execute_tool("get_pass_rates", {"lab": "lab-04"})
        assert isinstance(result, list)

    def test_execute_get_top_learners_returns_data(self):
        """Test that get_top_learners returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_top_learners", {"lab": "lab-04", "limit": 5})
        assert isinstance(result, list)

    def test_execute_get_groups_returns_data(self):
        """Test that get_groups returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_groups", {"lab": "lab-04"})
        assert isinstance(result, list)

    def test_execute_get_scores_returns_data(self):
        """Test that get_scores returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_scores", {"lab": "lab-04"})
        assert isinstance(result, list)

    def test_execute_get_timeline_returns_data(self):
        """Test that get_timeline returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_timeline", {"lab": "lab-04"})
        assert isinstance(result, list)

    def test_execute_get_completion_rate_returns_data(self):
        """Test that get_completion_rate returns data."""
        router = IntentRouter()
        result = router._execute_tool("get_completion_rate", {"lab": "lab-04"})
        assert isinstance(result, dict)
