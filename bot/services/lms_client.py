"""LMS API client for interacting with the backend."""

import httpx

from bot.config import settings


class LMSClient:
    """Client for the Learning Management System API."""

    def __init__(self):
        """Initialize the LMS client."""
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    def health_check(self) -> bool:
        """Check if the LMS API is reachable.

        Returns:
            True if the API is healthy, False otherwise
        """
        try:
            response = self.client.get("/health")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def get_labs(self) -> list[dict]:
        """Fetch available labs.

        Returns:
            List of lab dictionaries
        """
        try:
            response = self.client.get("/items")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return []

    def get_scores(self, lab_name: str | None = None) -> list[dict]:
        """Fetch user scores.

        Args:
            lab_name: Optional lab name to filter scores

        Returns:
            List of score dictionaries
        """
        try:
            endpoint = "/interactions"
            if lab_name:
                # Will be implemented with proper filtering in Task 2
                pass
            response = self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return []

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
