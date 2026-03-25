#!/usr/bin/env python3
"""CLI entry point for the LMS bot agent with documentation tools.

Usage:
    python agent.py "What labs are available?"
    python agent.py "/health"
    python agent.py "Read the file bot.py"
    python agent.py "List files in the current directory"

Returns JSON response with the bot's answer.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure the parent directory is in the Python path
bot_dir = Path(__file__).resolve().parent
parent_dir = bot_dir.parent
sys.path.insert(0, str(parent_dir))

from bot.handlers import handle_help, handle_health, handle_labs, handle_scores, handle_start
from bot.services.llm_client import LLMClient


# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the specified path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read (relative or absolute)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at the specified path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list (relative or absolute). Use '.' for current directory."
                    }
                },
                "required": ["path"]
            }
        }
    }
]

COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def read_file(path: str) -> dict[str, Any]:
    """Read the contents of a file.

    Args:
        path: Path to the file (relative or absolute)

    Returns:
        Dictionary with 'success' status and 'content' or 'error'
    """
    try:
        # Resolve path relative to bot directory if not absolute
        if not Path(path).is_absolute():
            resolved_path = bot_dir / path
        else:
            resolved_path = Path(path)

        # Security: ensure path is within project directory
        try:
            resolved_path.resolve().relative_to(parent_dir.resolve())
        except ValueError:
            return {
                "success": False,
                "error": f"Access denied: path must be within project directory"
            }

        if not resolved_path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}"
            }

        if resolved_path.is_dir():
            return {
                "success": False,
                "error": f"Path is a directory, not a file: {path}"
            }

        content = resolved_path.read_text(encoding="utf-8")
        return {
            "success": True,
            "content": content,
            "path": str(resolved_path)
        }

    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }


def list_files(path: str) -> dict[str, Any]:
    """List files and directories at the specified path.

    Args:
        path: Path to the directory (relative or absolute)

    Returns:
        Dictionary with 'success' status and 'files' list or 'error'
    """
    try:
        # Resolve path relative to bot directory if not absolute
        if not Path(path).is_absolute():
            resolved_path = bot_dir / path
        else:
            resolved_path = Path(path)

        # Security: ensure path is within project directory
        try:
            resolved_path.resolve().relative_to(parent_dir.resolve())
        except ValueError:
            return {
                "success": False,
                "error": f"Access denied: path must be within project directory"
            }

        if not resolved_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {path}"
            }

        if not resolved_path.is_dir():
            return {
                "success": False,
                "error": f"Path is a file, not a directory: {path}"
            }

        entries = []
        for entry in sorted(resolved_path.iterdir()):
            entry_type = "dir" if entry.is_dir() else "file"
            entries.append({
                "name": entry.name,
                "type": entry_type,
                "path": str(entry.relative_to(parent_dir))
            })

        return {
            "success": True,
            "files": entries,
            "directory": str(resolved_path)
        }

    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing directory: {str(e)}"
        }


# Tool function mapping
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
}


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool function with the given arguments.

    Args:
        name: Name of the tool to execute
        arguments: Arguments to pass to the tool

    Returns:
        Result from the tool execution
    """
    if name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown tool: {name}"
        }

    func = TOOL_FUNCTIONS[name]
    return func(**arguments)


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command from user input.

    Args:
        text: User input text

    Returns:
        Tuple of (command, arguments)
    """
    text = text.strip()

    if not text:
        return "", ""

    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return command, args

    return "", text


def handle_message(text: str) -> str:
    """Handle a user message and return a response.

    Args:
        text: User input text

    Returns:
        Response text
    """
    command, args = parse_command(text)

    if command in COMMAND_HANDLERS:
        handler = COMMAND_HANDLERS[command]
        return handler(args)

    if text:
        llm = LLMClient()
        intent = llm.classify_intent(text)

        if intent == "check_scores":
            return handle_scores(args or text)
        if intent == "list_labs":
            return handle_labs(text)
        if intent == "get_help":
            return handle_help(text)
        if intent == "health_check":
            return handle_health(text)

    return "I didn't understand that command. Use /help to see available commands."


def handle_with_tools(question: str) -> dict[str, Any]:
    """Handle a question using LLM function calling with tools.

    Args:
        question: User's question

    Returns:
        Dictionary with response and any tool results
    """
    llm = LLMClient()

    # Check if LLM is configured
    if not llm.base_url or not llm.api_key:
        # Fallback to keyword-based handling
        response = handle_message(question)
        return {
            "question": question,
            "response": response,
            "tool_used": None
        }

    try:
        # Call LLM with tools
        response = llm.client.post(
            "/v1/chat/completions",
            json={
                "model": llm.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a documentation assistant for a Learning Management System bot. "
                            "You have access to tools that can read files and list directories. "
                            "Use these tools to help users explore the codebase. "
                            "If the user asks to read a file, use read_file. "
                            "If the user asks to list files or see what's in a directory, use list_files."
                        ),
                    },
                    {"role": "user", "content": question},
                ],
                "tools": TOOLS,
                "tool_choice": "auto",
                "max_tokens": 1000,
            },
        )
        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]

        # Check if LLM wants to call a tool
        if "tool_calls" in message and message["tool_calls"]:
            tool_call = message["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            # Execute the tool
            tool_result = execute_tool(tool_name, tool_args)

            # Get final response from LLM with tool result
            final_response = llm.client.post(
                "/v1/chat/completions",
                json={
                    "model": llm.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a documentation assistant. Summarize the tool results for the user.",
                        },
                        {"role": "user", "content": question},
                        {
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps(tool_result, indent=2),
                        },
                    ],
                    "max_tokens": 1000,
                },
            )
            final_response.raise_for_status()
            final_data = final_response.json()
            response_text = final_data["choices"][0]["message"]["content"]

            return {
                "question": question,
                "response": response_text,
                "tool_used": tool_name,
                "tool_result": tool_result,
            }

        # No tool call, just return LLM response
        response_text = message.get("content", "I'm not sure how to help with that.")
        return {
            "question": question,
            "response": response_text,
            "tool_used": None,
        }

    except Exception as e:
        # Fallback to basic handling on error
        response = handle_message(question)
        return {
            "question": question,
            "response": response,
            "tool_used": None,
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "No question provided",
            "usage": "python agent.py <question>"
        }))
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    # Check if question is about file operations (use tools)
    file_keywords = ["read", "list", "show", "file", "directory", "folder", "contents"]
    if any(keyword in question.lower() for keyword in file_keywords):
        result = handle_with_tools(question)
    else:
        # Use basic command handling
        response = handle_message(question)
        result = {
            "question": question,
            "response": response,
            "tool_used": None,
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
