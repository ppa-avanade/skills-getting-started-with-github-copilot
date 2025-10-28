"""
Integration tests for the High School Management System API
"""

import pytest
from fastapi import status


class TestIntegrationWorkflows:
    """Integration tests that test complete workflows"""
    
    def test_complete_signup_and_removal_workflow(self, client):
        """Test complete workflow: signup, verify, remove, verify"""
        test_email = "integration_test@mergington.edu"
        activity_name = "Programming Class"
        
        # Step 1: Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_participants = initial_activities[activity_name]["participants"].copy()
        
        # Step 2: Sign up for activity
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Step 3: Verify signup
        verify_response = client.get("/activities")
        verify_activities = verify_response.json()
        assert test_email in verify_activities[activity_name]["participants"]
        assert len(verify_activities[activity_name]["participants"]) == len(initial_participants) + 1
        
        # Step 4: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )
        assert remove_response.status_code == status.HTTP_200_OK
        
        # Step 5: Verify removal
        final_response = client.get("/activities")
        final_activities = final_response.json()
        assert test_email not in final_activities[activity_name]["participants"]
        assert len(final_activities[activity_name]["participants"]) == len(initial_participants)
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity_name = "Gym Class"
        test_emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Sign up all test students
        for email in test_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all are signed up
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        
        for email in test_emails:
            assert email in final_participants
        
        assert len(final_participants) == initial_count + len(test_emails)
    
    def test_signup_remove_signup_again(self, client):
        """Test signing up, removing, then signing up again for same activity"""
        test_email = "repeat_test@mergington.edu"
        activity_name = "Basketball Club"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Remove
        response2 = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )
        assert response2.status_code == status.HTTP_200_OK
        
        # Signup again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response3.status_code == status.HTTP_200_OK
        
        # Verify final state
        final_response = client.get("/activities")
        final_activities = final_response.json()
        assert test_email in final_activities[activity_name]["participants"]


class TestErrorHandling:
    """Tests for various error conditions and edge cases"""
    
    def test_empty_activity_name(self, client, test_email):
        """Test handling of empty activity name"""
        response = client.post(
            "/activities//signup",
            params={"email": test_email}
        )
        # This should result in a 404 since the path doesn't match
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_special_characters_in_activity_name(self, client, test_email):
        """Test handling of special characters in activity name"""
        special_names = [
            "Art & Craft Club",
            "Math+Science",
            "Drama/Theater"
        ]
        
        for name in special_names:
            response = client.post(
                f"/activities/{name}/signup",
                params={"email": test_email}
            )
            # These should all return 404 since they don't exist
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_case_sensitive_activity_names(self, client, test_email):
        """Test that activity names are case sensitive"""
        # Try with different cases
        response1 = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": test_email}
        )
        assert response1.status_code == status.HTTP_404_NOT_FOUND
        
        response2 = client.post(
            "/activities/CHESS CLUB/signup",  # uppercase
            params={"email": test_email}
        )
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        
        # Correct case should work
        response3 = client.post(
            "/activities/Chess Club/signup",
            params={"email": test_email}
        )
        assert response3.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestDataValidation:
    """Tests for data validation"""
    
    def test_email_parameter_required(self, client):
        """Test that email parameter is required"""
        response = client.post("/activities/Chess Club/signup")
        # FastAPI should return 422 for missing required parameter
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_empty_email_parameter(self, client):
        """Test handling of empty email parameter"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        # Should still process but with empty email
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_activity_data_persistence(self, client):
        """Test that activity data persists across multiple requests"""
        # Make multiple requests and ensure data is consistent
        responses = []
        for _ in range(3):
            response = client.get("/activities")
            responses.append(response.json())
        
        # All responses should be identical
        for i in range(1, len(responses)):
            assert responses[i] == responses[0]
    
    def test_participant_list_modifications(self, client):
        """Test that participant lists are properly modified"""
        test_email = "list_test@mergington.edu"
        activity_name = "Science Club"
        
        # Get initial list
        initial_response = client.get("/activities")
        initial_list = initial_response.json()[activity_name]["participants"].copy()
        
        # Add participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Check list was modified
        after_add_response = client.get("/activities")
        after_add_list = after_add_response.json()[activity_name]["participants"]
        
        assert len(after_add_list) == len(initial_list) + 1
        assert test_email in after_add_list
        
        # Remove participant
        client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )
        
        # Check list was restored
        after_remove_response = client.get("/activities")
        after_remove_list = after_remove_response.json()[activity_name]["participants"]
        
        assert len(after_remove_list) == len(initial_list)
        assert test_email not in after_remove_list