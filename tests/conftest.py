import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient with a clean activities state.
    
    Arranges: Creates a snapshot of the original activities state
    Yields: A TestClient for making requests
    Cleans up: Restores activities to the original snapshot after each test
    """
    # Arrange: Save original state
    original_activities = copy.deepcopy(activities)
    
    # Yield the test client
    yield TestClient(app)
    
    # Cleanup: Restore original state
    activities.clear()
    activities.update(original_activities)
