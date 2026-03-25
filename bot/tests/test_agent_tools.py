"""Tests for agent.py documentation tools."""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
bot_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(bot_dir))

# Import tool functions directly for testing
from agent import read_file, list_files, TOOL_FUNCTIONS, TOOLS


class TestToolDefinitions:
    """Tests for tool schema definitions."""

    def test_tools_list_not_empty(self):
        """Test that TOOLS list is defined and not empty."""
        assert len(TOOLS) >= 2

    def test_read_file_tool_exists(self):
        """Test that read_file tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOLS]
        assert "read_file" in tool_names

    def test_list_files_tool_exists(self):
        """Test that list_files tool is defined."""
        tool_names = [t["function"]["name"] for t in TOOLS]
        assert "list_files" in tool_names

    def test_read_file_tool_has_required_parameters(self):
        """Test that read_file tool has required path parameter."""
        read_file_tool = next(
            t for t in TOOLS if t["function"]["name"] == "read_file"
        )
        params = read_file_tool["function"]["parameters"]
        assert "path" in params["required"]
        assert "path" in params["properties"]

    def test_list_files_tool_has_required_parameters(self):
        """Test that list_files tool has required path parameter."""
        list_files_tool = next(
            t for t in TOOLS if t["function"]["name"] == "list_files"
        )
        params = list_files_tool["function"]["parameters"]
        assert "path" in params["required"]
        assert "path" in params["properties"]


class TestReadFileTool:
    """Tests for the read_file tool function."""

    def test_read_file_function_exists(self):
        """Test that read_file function exists in TOOL_FUNCTIONS."""
        assert "read_file" in TOOL_FUNCTIONS

    def test_read_file_existing_file(self):
        """Test reading an existing file."""
        result = read_file("agent.py")
        assert result["success"] is True
        assert "content" in result
        assert len(result["content"]) > 0

    def test_read_file_nonexistent_file(self):
        """Test reading a non-existent file."""
        result = read_file("nonexistent_file_xyz.txt")
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_read_file_directory_path(self):
        """Test reading a directory (should fail)."""
        result = read_file("tests")
        assert result["success"] is False
        assert "error" in result

    def test_read_file_returns_path(self):
        """Test that read_file result includes the path."""
        result = read_file("agent.py")
        assert "path" in result


class TestListFilesTool:
    """Tests for the list_files tool function."""

    def test_list_files_function_exists(self):
        """Test that list_files function exists in TOOL_FUNCTIONS."""
        assert "list_files" in TOOL_FUNCTIONS

    def test_list_files_existing_directory(self):
        """Test listing an existing directory."""
        result = list_files(".")
        assert result["success"] is True
        assert "files" in result
        assert isinstance(result["files"], list)
        assert len(result["files"]) > 0

    def test_list_files_returns_file_info(self):
        """Test that list_files returns file information."""
        result = list_files(".")
        assert result["success"] is True
        # Check that at least one file has required fields
        for file_info in result["files"]:
            assert "name" in file_info
            assert "type" in file_info

    def test_list_files_nonexistent_directory(self):
        """Test listing a non-existent directory."""
        result = list_files("nonexistent_directory_xyz")
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_list_files_file_path(self):
        """Test listing a file path (should fail)."""
        result = list_files("agent.py")
        assert result["success"] is False
        assert "error" in result


class TestExecuteTool:
    """Tests for the execute_tool function."""

    def test_execute_tool_unknown_tool(self):
        """Test executing an unknown tool."""
        from agent import execute_tool
        result = execute_tool("unknown_tool", {})
        assert result["success"] is False
        assert "error" in result

    def test_execute_tool_read_file(self):
        """Test executing read_file through execute_tool."""
        from agent import execute_tool
        result = execute_tool("read_file", {"path": "agent.py"})
        assert result["success"] is True
        assert "content" in result

    def test_execute_tool_list_files(self):
        """Test executing list_files through execute_tool."""
        from agent import execute_tool
        result = execute_tool("list_files", {"path": "."})
        assert result["success"] is True
        assert "files" in result
