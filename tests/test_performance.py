"""
Performance and load tests for the High School Management System API
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import status


class TestPerformance:
    """Performance tests for the API endpoints"""
    
    def test_activities_endpoint_response_time(self, client):
        """Test that activities endpoint responds within reasonable time"""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_multiple_concurrent_requests(self, client):
        """Test handling of multiple concurrent requests"""
        def make_request():
            return client.get("/activities")
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
        
        # All responses should be identical
        first_response = responses[0].json()
        for response in responses[1:]:
            assert response.json() == first_response
    
    def test_signup_under_load(self, client):
        """Test signup functionality under concurrent load"""
        base_email = "load_test_{i}@mergington.edu"
        activity_name = "Drama Society"
        num_requests = 5
        
        def signup_student(i):
            email = base_email.format(i=i)
            return client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Make concurrent signup requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(signup_student, i) for i in range(num_requests)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        success_count = sum(1 for response in responses if response.status_code == status.HTTP_200_OK)
        assert success_count == num_requests
        
        # Verify all participants were added
        final_response = client.get("/activities")
        participants = final_response.json()[activity_name]["participants"]
        
        for i in range(num_requests):
            email = base_email.format(i=i)
            assert email in participants


class TestScalability:
    """Tests for API scalability and limits"""
    
    def test_large_number_of_participants(self, client):
        """Test handling of activities with many participants"""
        activity_name = "Science Club"
        base_email = "scale_test_{i}@mergington.edu"
        num_participants = 50  # Add many participants
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Add many participants
        for i in range(num_participants):
            email = base_email.format(i=i)
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all were added
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert len(final_participants) == initial_count + num_participants
        
        # Test that we can still query activities efficiently
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 2.0  # Should still be fast
    
    def test_rapid_signup_removal_cycles(self, client):
        """Test rapid cycles of signup and removal"""
        activity_name = "Math Olympiad"
        test_email = "cycle_test@mergington.edu"
        num_cycles = 10
        
        for cycle in range(num_cycles):
            # Sign up
            signup_response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": test_email}
            )
            assert signup_response.status_code == status.HTTP_200_OK
            
            # Remove
            remove_response = client.delete(
                f"/activities/{activity_name}/remove",
                params={"email": test_email}
            )
            assert remove_response.status_code == status.HTTP_200_OK
        
        # Final state should be clean
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert test_email not in final_participants


class TestMemoryUsage:
    """Tests to ensure memory usage remains reasonable"""
    
    def test_memory_stability_with_many_operations(self, client):
        """Test that memory usage remains stable during many operations"""
        activity_name = "Programming Class"
        base_email = "memory_test_{i}@mergington.edu"
        
        # Perform many operations
        for i in range(100):
            email = base_email.format(i=i)
            
            # Sign up
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            # Check activities (simulates user browsing)
            client.get("/activities")
            
            # Remove every 10th participant to vary the data
            if i % 10 == 0 and i > 0:
                remove_email = base_email.format(i=i-5)
                client.delete(
                    f"/activities/{activity_name}/remove",
                    params={"email": remove_email}
                )
        
        # API should still be responsive
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        # Data should be consistent
        activities = response.json()
        assert activity_name in activities
        assert isinstance(activities[activity_name]["participants"], list)


class TestErrorRecovery:
    """Tests for error recovery and resilience"""
    
    def test_recovery_after_bad_requests(self, client):
        """Test that system recovers properly after bad requests"""
        # Make several bad requests
        bad_requests = [
            ("POST", "/activities/NonExistent/signup", {"email": "test@test.com"}, [404]),
            ("POST", "/activities/Chess Club/signup", {"email": "michael@mergington.edu"}, [400]),  # Already exists
            ("DELETE", "/activities/Chess Club/remove", {"email": "nonexistent@test.com"}, [400]),
        ]
        
        for method, endpoint, params, expected_codes in bad_requests:
            if method == "POST":
                response = client.post(endpoint, params=params)
            else:
                response = client.delete(endpoint, params=params)
            # These should fail, but not crash the system
            assert response.status_code in expected_codes
        
        # System should still work normally
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        # Normal operations should work
        test_response = client.post(
            "/activities/Art Club/signup",
            params={"email": "recovery_test@mergington.edu"}
        )
        assert test_response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_data_consistency_after_errors(self, client):
        """Test that data remains consistent even after errors"""
        activity_name = "Basketball Club"
        test_email = "consistency_test@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # Mix of good and bad operations
        operations = [
            ("signup", test_email, status.HTTP_200_OK),
            ("signup", test_email, status.HTTP_400_BAD_REQUEST),  # Duplicate
            ("remove", "nonexistent@test.com", status.HTTP_400_BAD_REQUEST),  # Not found
            ("remove", test_email, status.HTTP_200_OK),  # Valid removal
            ("remove", test_email, status.HTTP_400_BAD_REQUEST),  # Already removed
        ]
        
        for operation, email, expected_status in operations:
            if operation == "signup":
                response = client.post(
                    f"/activities/{activity_name}/signup",
                    params={"email": email}
                )
            else:
                response = client.delete(
                    f"/activities/{activity_name}/remove",
                    params={"email": email}
                )
            
            assert response.status_code == expected_status
        
        # Final state should be consistent with initial state
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert final_participants == initial_participants