"""
Tests for shared data models.
"""

import pytest
from datetime import datetime
from shared.models import (
    Query, Response, Task, Command, HealthStatus, 
    ErrorResponse, DocumentChunk, SearchResult
)


def test_query_model():
    """Test Query model validation."""
    query = Query(text="test query")
    assert query.text == "test query"
    assert query.context is None
    assert query.session_id is None
    assert isinstance(query.timestamp, datetime)


def test_response_model():
    """Test Response model validation."""
    response = Response(
        content="test response",
        confidence=0.8,
        source="test",
        processing_time=1.5
    )
    assert response.content == "test response"
    assert response.confidence == 0.8
    assert response.source == "test"
    assert response.processing_time == 1.5


def test_confidence_validation():
    """Test confidence score validation."""
    # Valid confidence scores
    Response(content="test", confidence=0.0, source="test", processing_time=1.0)
    Response(content="test", confidence=1.0, source="test", processing_time=1.0)
    
    # Invalid confidence scores should raise validation error
    with pytest.raises(ValueError):
        Response(content="test", confidence=-0.1, source="test", processing_time=1.0)
    
    with pytest.raises(ValueError):
        Response(content="test", confidence=1.1, source="test", processing_time=1.0)


def test_task_model():
    """Test Task model."""
    task = Task(type="log_analysis", params={"file": "/var/log/syslog"})
    assert task.type == "log_analysis"
    assert task.params["file"] == "/var/log/syslog"
    assert task.status == "pending"
    assert task.result is None


def test_command_model():
    """Test Command model."""
    command = Command(
        command="ls -la",
        preview="List directory contents"
    )
    assert command.command == "ls -la"
    assert command.preview == "List directory contents"
    assert command.safe is False
    assert command.executed is False


def test_health_status():
    """Test HealthStatus model."""
    health = HealthStatus()
    assert health.status == "ok"
    assert isinstance(health.timestamp, datetime)


def test_error_response():
    """Test ErrorResponse model."""
    error = ErrorResponse(
        error="Test error",
        code=500,
        details="Test details",
        suggestion="Try again"
    )
    assert error.error == "Test error"
    assert error.code == 500
    assert error.details == "Test details"
    assert error.suggestion == "Try again"