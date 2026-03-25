"""LMS API client for interacting with the backend."""

from dataclasses import dataclass

import httpx

from bot.config import settings


@dataclass
class LMSHealthStatus:
    """Health status of the LMS backend."""

    healthy: bool
    item_count: int | None = None
    error: str | None = None


@dataclass
class LabInfo:
    """Information about a lab."""

    id: int
    title: str
    description: str
    type: str


@dataclass
class TaskScore:
    """Score information for a task."""

    task: str
    avg_score: float
    attempts: int


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

    def _format_error(self, error: Exception) -> str:
        """Format an error message that includes the actual error details."""
        error_str = str(error).lower()

        if "connection refused" in error_str or "connect" in error_str:
            return f"connection refused ({self.base_url}). Check that the services are running."

        if "http" in error_str:
            if hasattr(error, "response") and error.response is not None:
                status = error.response.status_code
                reason = error.response.reason_phrase
                return f"HTTP {status} {reason}. The backend service may be down."
            if "502" in error_str or "bad gateway" in error_str:
                return "HTTP 502 Bad Gateway. The backend service may be down."
            if "503" in error_str or "service unavailable" in error_str:
                return "HTTP 503 Service Unavailable. The backend service may be down."
            if "401" in error_str or "unauthorized" in error_str:
                return "HTTP 401 Unauthorized. Check the API key configuration."
            if "403" in error_str or "forbidden" in error_str:
                return "HTTP 403 Forbidden. Check the API key configuration."
            if "404" in error_str or "not found" in error_str:
                return "HTTP 404 Not Found. The requested resource does not exist."
            if "500" in error_str or "internal server error" in error_str:
                return "HTTP 500 Internal Server Error. The backend encountered an error."

        if "timeout" in error_str or "timed out" in error_str:
            return f"request timed out ({self.base_url}). The backend may be overloaded."

        return str(error)

    def health_check(self) -> LMSHealthStatus:
        """Check if the LMS API is reachable and get item count."""
        try:
            response = self.client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return LMSHealthStatus(healthy=True, item_count=len(items))
        except httpx.HTTPError as e:
            return LMSHealthStatus(healthy=False, error=self._format_error(e))
        except Exception as e:
            return LMSHealthStatus(healthy=False, error=self._format_error(e))

    def get_items(self) -> list[dict]:
        """Get all items (labs and tasks)."""
        response = self.client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list[dict]:
        """Get enrolled learners."""
        response = self.client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict]:
        """Get score distribution for a lab."""
        response = self.client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Get per-task pass rates for a lab."""
        response = self.client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: str) -> list[dict]:
        """Get submission timeline for a lab."""
        response = self.client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict]:
        """Get per-group performance for a lab."""
        response = self.client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 10) -> list[dict]:
        """Get top learners for a lab."""
        response = self.client.get(
            "/analytics/top-learners", params={"lab": lab, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        response = self.client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger ETL pipeline sync."""
        response = self.client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
