"""LLM API client for intent classification and AI assistance with tool calling support."""

import json
from typing import Any

import httpx

from bot.config import settings


class LLMClient:
    """Client for the LLM API with tool calling support."""

    def __init__(self):
        """Initialize the LLM client."""
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url
        self.model = settings.llm_api_model
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(60.0, connect=10.0),
            )
        return self._client

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str | dict = "auto",
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Send a chat request with tool definitions.

        Args:
            messages: List of message dicts with role and content
            tools: List of tool definitions
            tool_choice: How to choose tools ("auto", "none", "required", or specific)
            max_tokens: Maximum tokens in response

        Returns:
            Response dict with message and optional tool_calls
        """
        if not self.base_url or not self.api_key:
            return {
                "error": "LLM not configured",
                "message": {"role": "assistant", "content": "LLM service is not configured."},
            }

        try:
            response = self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": tool_choice,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]
        except httpx.HTTPError as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"LLM service unavailable: {str(e)}"},
            }

    def classify_intent(self, user_message: str) -> str:
        """Classify the user's intent from their message.

        Args:
            user_message: The user's natural language message

        Returns:
            Intent string (e.g., "check_scores", "list_labs", "help")
        """
        if not self.base_url or not self.api_key:
            return self._classify_by_keywords(user_message)

        try:
            response = self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an intent classifier for a Learning Management System bot. "
                                "Classify the user's message into one of these intents: "
                                "check_scores, list_labs, submit_solution, get_help, health_check, other. "
                                "Respond with only the intent name."
                            ),
                        },
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 20,
                },
            )
            response.raise_for_status()
            data = response.json()
            intent = data["choices"][0]["message"]["content"].strip()
            return intent.lower()
        except httpx.HTTPError:
            return self._classify_by_keywords(user_message)

    def _classify_by_keywords(self, message: str) -> str:
        """Fallback keyword-based intent classification."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["score", "grade", "result"]):
            return "check_scores"
        if any(word in message_lower for word in ["lab", "task", "assignment"]):
            return "list_labs"
        if any(word in message_lower for word in ["help", "command", "what can"]):
            return "get_help"
        if any(word in message_lower for word in ["health", "status", "working"]):
            return "health_check"
        if any(word in message_lower for word in ["submit", "upload", "send"]):
            return "submit_solution"

        return "other"

    def generate_response(self, context: str, question: str) -> str:
        """Generate an AI response to a user question.

        Args:
            context: Additional context (e.g., lab info, user data)
            question: The user's question

        Returns:
            AI-generated response text
        """
        if not self.base_url or not self.api_key:
            return "AI assistance is not configured. Please contact support."

        try:
            response = self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant for a Learning Management System. "
                                "Help students with questions about labs, submissions, and course material. "
                                "Be concise and friendly."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Context: {context}\n\nQuestion: {question}",
                        },
                    ],
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPError as e:
            return f"AI service unavailable: {str(e)}"

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
