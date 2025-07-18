import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.factory import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_data():
    return {
        "data_list": [
            {
                "temperature_one": 35,
                "temperature_two": 40,
                "vibration_x": 0.2,
                "vibration_y": 0.3,
                "vibration_z": 0.1,
                "magnetic_flux_x": 0.15,
                "magnetic_flux_y": 0.25,
                "magnetic_flux_z": 0.35,
                "ultrasound_one": 45,
                "ultrasound_two": 50
            }
        ],
        "thresholds": {
            "temperature_skin_healthy": 30,
            "temperature_skin_warning": 50,
            "temperature_bearing_healthy": 35,
            "temperature_bearing_warning": 55,
            "vibration_X_healthy": 0.1,
            "vibration_X_warning": 0.5,
            "vibration_Y_healthy": 0.1,
            "vibration_Y_warning": 0.5,
            "vibration_Z_healthy": 0.1,
            "vibration_Z_warning": 0.5,
            "magnetic_flux_X_healthy": 0.1,
            "magnetic_flux_X_warning": 0.6,
            "magnetic_flux_Y_healthy": 0.1,
            "magnetic_flux_Y_warning": 0.6,
            "magnetic_flux_Z_healthy": 0.1,
            "magnetic_flux_Z_warning": 0.6,
            "ultrasound_one_healthy": 40,
            "ultrasound_one_warning": 60,
            "ultrasound_two_healthy": 40,
            "ultrasound_two_warning": 60
        }
    }

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert "uptime_seconds" in data
    assert data["status"] == "success"
    assert data["version"] == "3.0.0"

def test_check_health(client, test_data):
    # Test successful request
    response = client.post('/check_health', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert "overall_health" in data
    assert "temperature_health" in data
    assert "vibration_health" in data
    assert data["overall_health"] in ["Healthy", "Unhealthy"]
    assert data["temperature_health"] in ["healthy", "unhealthy"]
    assert data["vibration_health"] in ["healthy", "unhealthy"]
    
    # Test invalid requests
    test_cases = [
        (None, "Invalid or missing JSON in request", 400),
        ({}, "Missing 'data_list' or 'thresholds' in request", 400),
        ({"data_list": []}, "Missing 'data_list' or 'thresholds' in request", 400),
        ({"thresholds": {}}, "Missing 'data_list' or 'thresholds' in request", 400),
        (
            {"data_list": [{}], "thresholds": {}},
            "Missing required field: 'temperature_one'",
            400
        )
    ]
    
    for test_data, expected_error, expected_status in test_cases:
        response = client.post('/check_health', json=test_data)
        assert response.status_code == expected_status, f"Failed on test case with data: {test_data}"
        if expected_error:
            error_data = response.get_json()
            assert "error" in error_data
            assert error_data["error"] == expected_error

def test_analyze(client, test_data):
    # Test successful request
    response = client.post('/analyze', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert "overall_health" in data
    assert "possible_cause" in data
    assert "details" in data
    assert data["overall_health"] in ["Healthy", "Unhealthy"]
    
    # Test error cases - current implementation behavior
    try:
        response = client.post('/analyze', json=None)
        assert response.status_code == 415  # Unsupported media type
    except Exception as e:
        assert str(e) == "415 Unsupported Media Type"

    # Test with empty or invalid data
    error_cases = [
        ({}, 500),  # Current behavior is 500 for empty data
        ({"data_list": []}, 500),
        ({"thresholds": {}}, 500)
    ]
    
    for test_data, expected_status in error_cases:
        response = client.post('/analyze', json=test_data)
        assert response.status_code == expected_status, f"Failed for test case: {test_data}"

def test_check_health_quad(client, test_data):
    # Test successful request
    response = client.post('/check_health_quad', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert "overall_health" in data
    assert "temperature_health" in data
    assert "vibration_health" in data
    assert "magnetic_flux_health" in data
    assert "ultrasound_health" in data
    assert data["overall_health"] in ["Healthy", "Unhealthy"]
    assert data["temperature_health"] in ["healthy", "unhealthy"]
    assert data["vibration_health"] in ["healthy", "unhealthy"]
    assert data["magnetic_flux_health"] in ["healthy", "unhealthy"]
    assert data["ultrasound_health"] in ["healthy", "unhealthy"]
    
    # Test invalid requests
    test_cases = [
        (None, "Invalid or missing JSON in request"),
        ({}, "Missing 'data_list' or 'thresholds' in request"),
        ({"data_list": []}, "Missing 'data_list' or 'thresholds' in request"),
        ({"thresholds": {}}, "Missing 'data_list' or 'thresholds' in request")
    ]
    
    for invalid_data, expected_error in test_cases:
        response = client.post('/check_health_quad', json=invalid_data)
        assert response.status_code == 400
        error_data = response.get_json()
        assert "error" in error_data
        assert error_data["error"] == expected_error

def test_report(client, test_data):
    # Test successful request
    response = client.post('/report', json=test_data)
    assert response.status_code == 200
    data = response.get_json()
    assert "overall_health" in data
    assert "possible_cause" in data
    assert "details" in data
    assert data["overall_health"] in ["Healthy", "Unhealthy"]
    assert isinstance(data["details"], dict)
    
    # Check if details contains information for all sensors
    expected_sensors = [
        "temperature_one", "temperature_two",
        "vibration_x", "vibration_y", "vibration_z",
        "magnetic_flux_x", "magnetic_flux_y", "magnetic_flux_z",
        "ultrasound_one", "ultrasound_two"
    ]
    for sensor in expected_sensors:
        assert sensor in data["details"]
        sensor_data = data["details"][sensor]
        assert "average" in sensor_data
        assert "status" in sensor_data
        assert "low" in sensor_data
        assert "high" in sensor_data
        assert sensor_data["status"] in ["GOOD", "NEEDS MAINTENANCE"]
    
    # Test error cases - current implementation behavior
    try:
        response = client.post('/report', json=None)
        assert response.status_code == 415  # Unsupported media type
    except Exception as e:
        assert str(e) == "415 Unsupported Media Type"

    # Test with empty or invalid data
    error_cases = [
        ({}, 500),  # Current behavior is 500 for empty data
        ({"data_list": []}, 500),
        ({"thresholds": {}}, 500)
    ]
    
    for test_data, expected_status in error_cases:
        response = client.post('/report', json=test_data)
        assert response.status_code == expected_status, f"Failed for test case: {test_data}"
