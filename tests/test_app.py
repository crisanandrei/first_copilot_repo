"""
Backend tests for the Mergington High School API using AAA pattern.
Each test clearly separates Arrange, Act, and Assert phases.
"""


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Test client ready
        Act: Make GET request to /activities
        Assert: Response contains at least the core activities
        """
        # Arrange
        expected_core_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Check that all core activities are present
        assert set(expected_core_activities).issubset(set(data.keys()))
        # Check that we have at least some activities
        assert len(data) >= 3
    
    def test_get_activities_contains_activity_details(self, client):
        """
        Arrange: Test client ready
        Act: Make GET request to /activities
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, details in data.items():
            assert set(details.keys()) == required_fields


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_succeeds(self, client):
        """
        Arrange: New email not yet in any activity
        Act: POST signup request with new email
        Assert: Response is successful and participant appears in activity
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "alice@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant is in the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert new_email in activities_data[activity_name]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity name that does not exist
        Act: POST signup request to non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        nonexistent_activity = "Unicorn Club"
        email = "bob@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_remove_participant_succeeds(self, client):
        """
        Arrange: Get an existing participant from an activity
        Act: DELETE request to remove that participant
        Assert: Participant is removed from the activity
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant is no longer in the activity
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert existing_email not in final_data[activity_name]["participants"]
        assert len(final_data[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Email that is not signed up for an activity
        Act: DELETE request to remove non-existent participant
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        activity_name = "Programming Class"
        nonexistent_email = "charlie@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": nonexistent_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    
    def test_remove_participant_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity that does not exist
        Act: DELETE request to remove participant from non-existent activity
        Assert: Response is 404 with appropriate error message
        """
        # Arrange
        nonexistent_activity = "Debate Club"
        email = "dave@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestSignupWorkflow:
    """Integration tests for signup/removal workflow"""
    
    def test_signup_then_remove_workflow(self, client):
        """
        Arrange: New participant
        Act: Sign up, verify presence, then remove
        Assert: Participant appears after signup and disappears after removal
        """
        # Arrange
        activity_name = "Gym Class"
        new_email = "emma@example.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert: Signup succeeded
        assert signup_response.status_code == 200
        
        # Act: Verify participant is now in the activity
        get_response = client.get("/activities")
        assert new_email in get_response.json()[activity_name]["participants"]
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": new_email}
        )
        
        # Assert: Removal succeeded
        assert remove_response.status_code == 200
        
        # Assert: Participant is no longer in the activity
        final_response = client.get("/activities")
        assert new_email not in final_response.json()[activity_name]["participants"]
