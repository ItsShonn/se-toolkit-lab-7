"""Intent router with LLM-powered tool calling for the LMS bot.

This module provides the core routing logic that:
1. Defines all 9 backend endpoints as LLM tools
2. Routes user messages to the LLM with tool definitions
3. Executes tool calls returned by the LLM
4. Feeds results back to the LLM for final answer generation
"""

import json
import sys
from typing import Any

from bot.services.llm_client import LLMClient
from bot.services.lms_client import LMSClient


# Tool definitions for all 9 backend endpoints
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get all labs and tasks. Use this to list available labs or find lab IDs.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled learners with their student groups.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets: 0-25, 26-50, 51-75, 76-100) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance (average score and student count) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by average score for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 10)"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate (percentage of learners who scored >= 60) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline sync to refresh data from autochecker.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the intent router
SYSTEM_PROMPT = """You are an intelligent assistant for a Learning Management System. 
You have access to tools that can fetch data about labs, learners, scores, and analytics.

When a user asks a question:
1. First understand what information they need
2. Call the appropriate tool(s) to get that information
3. If you need to compare labs or find the best/worst, first get the list of labs, then fetch data for each
4. Summarize the results in a clear, helpful way

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab (4 buckets)
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N learners for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

For questions like "which lab has the lowest pass rate":
1. First call get_items to get all labs
2. Then call get_pass_rates for EACH lab one by one
3. Keep calling tools until you have data for all labs
4. Compare the results and identify the lowest
5. Report the answer with specific numbers

IMPORTANT: When comparing multiple items, you MUST call tools for ALL items before summarizing.
Do not stop after just 2-3 items. Continue calling tools until you have all the data you need.
Only provide a final answer when you have collected all necessary data.

Always be specific with numbers when available. If data is empty, say so clearly."""


class IntentRouter:
    """Routes user messages to LLM with tool calling capability."""

    def __init__(self, debug: bool = False):
        """Initialize the intent router.

        Args:
            debug: If True, print debug output to stderr
        """
        self.llm = LLMClient()
        self.lms = LMSClient()
        self.debug = debug

    def _log(self, message: str) -> None:
        """Print debug message to stderr if debug mode is enabled."""
        if self.debug:
            print(message, file=sys.stderr)

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the appropriate LMS API method.

        Args:
            name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            Result from the tool execution
        """
        tool_methods = {
            "get_items": lambda: self.lms.get_items(),
            "get_learners": lambda: self.lms.get_learners(),
            "get_scores": lambda: self.lms.get_scores(arguments.get("lab", "")),
            "get_pass_rates": lambda: self.lms.get_pass_rates(arguments.get("lab", "")),
            "get_timeline": lambda: self.lms.get_timeline(arguments.get("lab", "")),
            "get_groups": lambda: self.lms.get_groups(arguments.get("lab", "")),
            "get_top_learners": lambda: self.lms.get_top_learners(
                arguments.get("lab", ""), arguments.get("limit", 10)
            ),
            "get_completion_rate": lambda: self.lms.get_completion_rate(
                arguments.get("lab", "")
            ),
            "trigger_sync": lambda: self.lms.trigger_sync(),
        }

        if name not in tool_methods:
            return {"error": f"Unknown tool: {name}"}

        try:
            result = tool_methods[name]()
            self._log(f"[tool] Result: {len(result) if isinstance(result, (list, dict)) else 'OK'} items")
            return result
        except Exception as e:
            self._log(f"[tool] Error: {str(e)}")
            return {"error": str(e)}

    def route(self, message: str) -> str:
        """Route a user message through the LLM with tool calling.

        Args:
            message: User's message

        Returns:
            Response text
        """
        # Check for gibberish, very short messages, or non-questions first
        message_lower = message.lower().strip()
        
        # Short gibberish detection
        if len(message) < 5:
            return self._fallback_response(message)
        
        # Known gibberish patterns
        gibberish_patterns = ["asdf", "test", "abc", "xyz", "asdfgh", "qwer", "zxcv"]
        if any(p in message_lower for p in gibberish_patterns):
            return self._fallback_response(message)
        
        # Check if message looks like a question or request (has question words or data-related terms)
        question_indicators = ["what", "which", "how", "show", "list", "get", "find", 
                               "who", "when", "where", "why", "tell", "compare", 
                               "lab", "score", "student", "group", "rate", "top",
                               "available", "enrolled", "completion", "timeline"]
        
        has_question_indicator = any(indicator in message_lower for indicator in question_indicators)
        
        # If no question indicators, use fallback
        if not has_question_indicator:
            return self._fallback_response(message)

        # Check if LLM is configured
        if not self.llm.base_url or not self.llm.api_key:
            return self._fallback_response(message)

        # Initialize conversation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        # Tool calling loop (max iterations to prevent infinite loops)
        max_iterations = 25
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM with tools - always use "auto" to let LLM decide
            self._log(f"[LLM] Calling with {len(messages)} messages (tool_choice=auto)")
            response = self.llm.chat_with_tools(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )

            # Check for error
            if "error" in response and response.get("error") == "LLM not configured":
                return self._fallback_response(message)

            # Get the assistant message
            assistant_message = response.get("message", response)
            messages.append(assistant_message)

            # Check if LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])
            content = assistant_message.get("content", "")

            self._log(f"[LLM] Response: tool_calls={len(tool_calls)}, content_len={len(content) if content else 0}")

            if not tool_calls:
                # No tool calls - check if LLM is providing final answer or just thinking
                if content and len(content) > 100:
                    # Likely a final answer
                    return content
                # LLM is thinking but not calling tools - prompt it to continue
                self._log(f"[LLM] Thinking without tool call, prompting to continue")
                messages.append({
                    "role": "user",
                    "content": "Continue: Call the next tool to get more data, or provide your final answer if you have enough information."
                })
                continue

            # Execute tool calls and collect results
            self._log(f"[summary] LLM requested {len(tool_calls)} tool call(s)")
            tool_results = []

            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "unknown")
                tool_args = json.loads(function.get("arguments", "{}"))

                self._log(f"[tool] LLM called: {tool_name}({json.dumps(tool_args)})")

                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)

                # Add tool result to messages with a reminder to continue
                tool_results.append({
                    "name": tool_name,
                    "result": result,
                })

                # Add tool response message for LLM with continuation hint
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": f"Result: {json.dumps(result, default=str)}\n\nContinue fetching data for remaining labs if needed, or provide final answer if you have all the data.",
                })

            self._log(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")

        # If we reach here, we hit max iterations
        return "I'm still working on that. Let me summarize what I found so far. Please try rephrasing your question."

    def _fallback_response(self, message: str) -> str:
        """Generate a fallback response when LLM is not available or input is unclear.

        Args:
            message: User's message

        Returns:
            Fallback response text
        """
        message_lower = message.lower()

        # Check for greetings
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]):
            return "Hello! I'm your LMS assistant. I can help you with:\n• Viewing available labs\n• Checking scores and pass rates\n• Finding top learners\n• Comparing group performance\n\nTry asking something like 'what labs are available?' or 'show me scores for lab 4'"

        # Check for gibberish or very short messages
        if len(message) < 4 or message_lower in ["asdf", "test", "abc", "xyz", "asdfgh"]:
            return "I didn't understand that. Here's what I can help you with:\n• /labs - List available labs\n• /scores <lab> - View scores for a lab\n• /health - Check backend status\n\nOr ask questions like 'which lab has the lowest pass rate?'"

        # Check for lab references without clear intent
        if "lab" in message_lower:
            return f"I see you mentioned a lab. I can help you with:\n• View pass rates: /scores <lab-name>\n• View available labs: /labs\n• Check backend status: /health\n\nWhat would you like to know?"

        # Default fallback
        return "I'm not sure I understand. Try:\n• 'what labs are available?'\n• 'show me scores for lab 4'\n• 'which lab has the lowest pass rate?'\n• 'who are the top students?'"


# Global router instance
_router: IntentRouter | None = None


def get_router(debug: bool = False) -> IntentRouter:
    """Get or create the global intent router instance.

    Args:
        debug: If True, enable debug output

    Returns:
        IntentRouter instance
    """
    global _router
    if _router is None or _router.debug != debug:
        _router = IntentRouter(debug=debug)
    return _router


def route_message(message: str, debug: bool = False) -> str:
    """Route a message through the intent router.

    Args:
        message: User's message
        debug: If True, enable debug output

    Returns:
        Response text
    """
    router = get_router(debug=debug)
    return router.route(message)
