"""
Business logic tests for the High School Management System API
"""

import pytest
from fastapi import status


class TestBusinessRules:
    """Tests for business logic and rules"""
    
    def test_all_required_activities_exist(self, client):
        """Test that all expected school activities are available"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check for core academic activities
        academic_activities = ["Chess Club", "Programming Class", "Math Olympiad", "Science Club"]
        for activity in academic_activities:
            assert activity in activities, f"Academic activity '{activity}' is missing"
        
        # Check for sports activities
        sports_activities = ["Gym Class", "Soccer Team", "Basketball Club"]
        for activity in sports_activities:
            assert activity in activities, f"Sports activity '{activity}' is missing"
        
        # Check for creative activities
        creative_activities = ["Art Club", "Drama Society"]
        for activity in creative_activities:
            assert activity in activities, f"Creative activity '{activity}' is missing"
    
    def test_activity_capacity_limits(self, client):
        """Test that activities have reasonable capacity limits"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])
            
            # All activities should have reasonable limits
            assert max_participants >= 10, f"Activity '{activity_name}' has too low capacity"
            assert max_participants <= 50, f"Activity '{activity_name}' has too high capacity"
            
            # Current participants should not exceed maximum
            assert current_participants <= max_participants, \
                f"Activity '{activity_name}' has too many participants"
    
    def test_school_email_domain_validation(self, client):
        """Test that the system accepts school email domains"""
        school_emails = [
            "student@mergington.edu",
            "teacher@mergington.edu",
            "admin@mergington.edu"
        ]
        
        for email in school_emails:
            response = client.post(
                "/activities/Art Club/signup",
                params={"email": email}
            )
            # Should succeed or fail due to duplicate, not email format
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_activity_scheduling_information(self, client):
        """Test that all activities have proper scheduling information"""
        response = client.get("/activities")
        activities = response.json()
        
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]
            
            # Schedule should contain a day of the week
            has_day = any(day in schedule for day in days_of_week)
            assert has_day, f"Activity '{activity_name}' schedule missing day of week"
            
            # Schedule should contain time information
            has_time = "PM" in schedule or "AM" in schedule
            assert has_time, f"Activity '{activity_name}' schedule missing time information"


class TestStudentExperience:
    """Tests from the student's perspective"""
    
    def test_student_can_view_all_activities(self, client):
        """Test that students can see all available activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        activities = response.json()
        assert len(activities) >= 9  # We know there are 9 activities
        
        # Each activity should have essential information
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Descriptions should be informative
            assert len(activity_data["description"]) > 10
    
    def test_student_signup_journey(self, client):
        """Test complete student signup journey"""
        student_email = "new_student@mergington.edu"
        chosen_activity = "Drama Society"
        
        # Step 1: Student views available activities
        activities_response = client.get("/activities")
        assert activities_response.status_code == status.HTTP_200_OK
        activities = activities_response.json()
        assert chosen_activity in activities
        
        # Step 2: Student signs up for an activity
        signup_response = client.post(
            f"/activities/{chosen_activity}/signup",
            params={"email": student_email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        assert "Signed up" in signup_response.json()["message"]
        
        # Step 3: Student verifies their enrollment
        verify_response = client.get("/activities")
        verify_activities = verify_response.json()
        assert student_email in verify_activities[chosen_activity]["participants"]
        
        # Step 4: Student decides to leave the activity
        removal_response = client.delete(
            f"/activities/{chosen_activity}/remove",
            params={"email": student_email}
        )
        assert removal_response.status_code == status.HTTP_200_OK
        
        # Step 5: Student verifies they're no longer enrolled
        final_response = client.get("/activities")
        final_activities = final_response.json()
        assert student_email not in final_activities[chosen_activity]["participants"]
    
    def test_student_multiple_activity_participation(self, client):
        """Test that students can participate in multiple activities"""
        student_email = "multi_activity@mergington.edu"
        activities_to_join = ["Art Club", "Science Club", "Programming Class"]
        
        # Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": student_email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify enrollment in all activities
        verify_response = client.get("/activities")
        all_activities = verify_response.json()
        
        for activity in activities_to_join:
            assert student_email in all_activities[activity]["participants"]


class TestTeacherAdministration:
    """Tests from the teacher/administrator perspective"""
    
    def test_view_activity_enrollment(self, client):
        """Test that administrators can view enrollment for all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            max_participants = activity_data["max_participants"]
            
            # Should be able to see current enrollment
            current_enrollment = len(participants)
            available_spots = max_participants - current_enrollment
            
            assert current_enrollment >= 0
            assert available_spots >= 0
            
            # All participant emails should look valid
            for email in participants:
                assert "@" in email
                assert "." in email
    
    def test_manage_student_enrollment(self, client):
        """Test administrative management of student enrollment"""
        student_email = "admin_managed@mergington.edu"
        activity_name = "Math Olympiad"
        
        # Admin adds student to activity
        add_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        assert add_response.status_code == status.HTTP_200_OK
        
        # Admin removes student from activity
        remove_response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": student_email}
        )
        assert remove_response.status_code == status.HTTP_200_OK
        
        # Verify student is no longer in activity
        verify_response = client.get("/activities")
        activities = verify_response.json()
        assert student_email not in activities[activity_name]["participants"]


class TestSystemReliability:
    """Tests for system reliability and edge cases"""
    
    def test_activity_names_are_consistent(self, client):
        """Test that activity names are consistent across requests"""
        # Make multiple requests and ensure activity names don't change
        responses = []
        for _ in range(5):
            response = client.get("/activities")
            responses.append(set(response.json().keys()))
        
        # All responses should have the same activity names
        first_set = responses[0]
        for response_set in responses[1:]:
            assert response_set == first_set
    
    def test_participant_data_integrity(self, client):
        """Test that participant data maintains integrity"""
        response = client.get("/activities")
        activities = response.json()
        
        all_participants = []
        for activity_data in activities.values():
            participants = activity_data["participants"]
            
            # No duplicates within an activity
            assert len(participants) == len(set(participants))
            
            # All participants should have valid email format
            for email in participants:
                assert "@" in email
                assert len(email) > 5  # Basic length check
            
            all_participants.extend(participants)
        
        # Same student can be in multiple activities (this is allowed)
        # So we don't check for uniqueness across all activities
    
    def test_api_response_format_consistency(self, client):
        """Test that API responses have consistent format"""
        # Test activities endpoint
        activities_response = client.get("/activities")
        assert activities_response.status_code == status.HTTP_200_OK
        assert activities_response.headers["content-type"] == "application/json"
        
        # Test signup endpoint
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "format_test@mergington.edu"}
        )
        if signup_response.status_code == status.HTTP_200_OK:
            assert "message" in signup_response.json()
        
        # Test remove endpoint
        remove_response = client.delete(
            "/activities/Chess Club/remove",
            params={"email": "format_test@mergington.edu"}
        )
        if remove_response.status_code == status.HTTP_200_OK:
            assert "message" in remove_response.json()