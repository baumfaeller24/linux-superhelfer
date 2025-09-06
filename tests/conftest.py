"""
Pytest configuration and fixtures for Linux Superhelfer tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    from shared.models import Query
    return Query(text="How do I check disk usage?", context="Linux administration")


@pytest.fixture
def sample_response():
    """Sample response for testing."""
    from shared.models import Response
    return Response(
        content="Use 'df -h' to check disk usage",
        confidence=0.9,
        source="core",
        processing_time=0.5
    )