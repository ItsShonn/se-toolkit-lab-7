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
        """Format an error message that includes the actual error details.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message with actual error details
        """
        error_str = str(error).lower()

        # Connection errors
        if "connection refused" in error_str or "connect" in error_str:
            return f"connection refused ({self.base_url}). Check that the services are running."

        # HTTP errors
        if "http" in error_str:
            # Try to extract status code from the error
            if hasattr(error, "response") and error.response is not None:
                status = error.response.status_code
                reason = error.response.reason_phrase
                return f"HTTP {status} {reason}. The backend service may be down."
            if "502" in error_str or "bad gateway" in error_str.lower():
                return "HTTP 502 Bad Gateway. The backend service may be down."
            if "503" in error_str or "service unavailable" in error_str.lower():
                return "HTTP 503 Service Unavailable. The backend service may be down."
            if "401" in error_str or "unauthorized" in error_str.lower():
                return "HTTP 401 Unauthorized. Check the API key configuration."
            if "403" in error_str or "forbidden" in error_str.lower():
                return "HTTP 403 Forbidden. Check the API key configuration."
            if "404" in error_str or "not found" in error_str.lower():
                return "HTTP 404 Not Found. The requested resource does not exist."
            if "500" in error_str or "internal server error" in error_str.lower():
                return "HTTP 500 Internal Server Error. The backend encountered an error."

        # Timeout errors
        if "timeout" in error_str or "timed out" in error_str:
            return f"request timed out ({self.base_url}). The backend may be overloaded."

        # Generic error - include the actual error message
        return str(error)

    def health_check(self) -> LMSHealthStatus:
        """Check if the LMS API is reachable and get item count.

        Returns:
            LMSHealthStatus with health information
        """
        try:
            response = self.client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return LMSHealthStatus(healthy=True, item_count=len(items))
        except httpx.HTTPError as e:
            return LMSHealthStatus(
                healthy=False, error=self._format_error(e)
            )
        except Exception as e:
            return LMSHealthStatus(
                healthy=False, error=self._format_error(e)
            )

    def get_labs(self) -> list[LabInfo]:
        """Fetch available labs.

        Returns:
            List of LabInfo objects
        """
        try:
            response = self.client.get("/items/")
            response.raise_for_status()
            items = response.json()
            labs = []
            for item in items:
                if item.get("type") == "lab":
                    labs.append(
                        LabInfo(
                            id=item["id"],
                            title=item["title"],
                            description=item.get("description", ""),
                            type=item["type"],
                        )
                    )
            return labs
        except httpx.HTTPError as e:
            raise RuntimeError(self._format_error(e)) from e
        except Exception as e:
            raise RuntimeError(self._format_error(e)) from e

    def get_pass_rates(self, lab_name: str) -> list[TaskScore]:
        """Fetch per-task pass rates for a lab.

        Args:
            lab_name: Lab identifier (e.g., "lab-04")

        Returns:
            List of TaskScore objects
        """
        try:
            response = self.client.get(
                "/analytics/pass-rates", params={"lab": lab_name}
            )
            response.raise_for_status()
            data = response.json()
            scores = []
            for item in data:
                scores.append(
                    TaskScore(
                        task=item["task"],
                        avg_score=float(item["avg_score"]),
                        attempts=int(item["attempts"]),
                    )
                )
            return scores
        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 400:
                    raise ValueError(f"Lab '{lab_name}' not found") from e
            raise RuntimeError(self._format_error(e)) from e
        except Exception as e:
            raise RuntimeError(self._format_error(e)) from e

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None
