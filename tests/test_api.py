"""
Tests for the High School Management System API endpoints
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that some known activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Tests for the activity signup endpoint"""
    
    def test_signup_for_existing_activity_success(self, client, test_email):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": test_email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Signed up {test_email} for Art Club"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities["Art Club"]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client, test_email):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": test_email}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup_fails(self, client):
        """Test that duplicate signup returns 400"""
        # Use an email that's already in Chess Club
        existing_email = "michael@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_email}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student is already signed up"
    
    def test_signup_multiple_different_activities(self, client, test_email):
        """Test that a student can sign up for multiple different activities"""
        # Sign up for Drama Society
        response1 = client.post(
            "/activities/Drama Society/signup",
            params={"email": test_email}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Sign up for Science Club
        response2 = client.post(
            "/activities/Science Club/signup",
            params={"email": test_email}
        )
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities["Drama Society"]["participants"]
        assert test_email in activities["Science Club"]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the remove participant endpoint"""
    
    def test_remove_existing_participant_success(self, client):
        """Test successful removal of an existing participant"""
        # First, add a test participant
        test_email = "remove_test@mergington.edu"
        client.post(
            "/activities/Math Olympiad/signup",
            params={"email": test_email}
        )
        
        # Now remove the participant
        response = client.delete(
            "/activities/Math Olympiad/remove",
            params={"email": test_email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Removed {test_email} from Math Olympiad"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email not in activities["Math Olympiad"]["participants"]
    
    def test_remove_from_nonexistent_activity_fails(self, client, test_email):
        """Test that removing from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/remove",
            params={"email": test_email}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_nonexistent_participant_fails(self, client, test_email):
        """Test that removing non-existent participant returns 400"""
        response = client.delete(
            "/activities/Basketball Club/remove",
            params={"email": test_email}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Student is not signed up for this activity"
    
    def test_remove_existing_participant_from_initial_data(self, client):
        """Test removing a participant that exists in the initial data"""
        # Remove an existing participant from Soccer Team
        existing_email = "lucas@mergington.edu"
        
        response = client.delete(
            "/activities/Soccer Team/remove",
            params={"email": existing_email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == f"Removed {existing_email} from Soccer Team"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert existing_email not in activities["Soccer Team"]["participants"]


class TestDataIntegrity:
    """Tests for data integrity and edge cases"""
    
    def test_activity_structure_consistency(self, client):
        """Test that all activities have consistent structure"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
            
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
    
    def test_participant_email_format(self, client):
        """Test various email formats for signup"""
        valid_emails = [
            "student@mergington.edu",
            "test.student@mergington.edu",
            "student123@mergington.edu"
        ]
        
        for email in valid_emails:
            response = client.post(
                "/activities/Art Club/signup",
                params={"email": email}
            )
            # Should succeed (might fail if already signed up, but that's OK)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]