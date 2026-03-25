"""Tests for the LMS API client."""

import pytest

from bot.services.lms_client import LMSClient, LMSHealthStatus, LabInfo, TaskScore


class TestLMSClientInit:
    """Tests for LMSClient initialization."""

    def test_client_initializes(self):
        """Test that LMSClient can be initialized."""
        client = LMSClient()
        assert client is not None

    def test_client_has_base_url(self):
        """Test that LMSClient has a base URL configured."""
        client = LMSClient()
        assert client.base_url is not None


class TestLMSHealthStatus:
    """Tests for LMSHealthStatus dataclass."""

    def test_health_status_healthy(self):
        """Test creating a healthy status."""
        status = LMSHealthStatus(healthy=True, item_count=42)
        assert status.healthy is True
        assert status.item_count == 42

    def test_health_status_unhealthy(self):
        """Test creating an unhealthy status."""
        status = LMSHealthStatus(healthy=False, error="connection refused")
        assert status.healthy is False
        assert status.error == "connection refused"


class TestLabInfo:
    """Tests for LabInfo dataclass."""

    def test_lab_info_creation(self):
        """Test creating a LabInfo object."""
        lab = LabInfo(id=1, title="Lab 01", description="Test lab", type="lab")
        assert lab.id == 1
        assert lab.title == "Lab 01"
        assert lab.type == "lab"


class TestTaskScore:
    """Tests for TaskScore dataclass."""

    def test_task_score_creation(self):
        """Test creating a TaskScore object."""
        score = TaskScore(task="Task 1", avg_score=75.5, attempts=100)
        assert score.task == "Task 1"
        assert score.avg_score == 75.5
        assert score.attempts == 100
