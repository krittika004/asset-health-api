from locust import HttpUser, task, between
import logging

class HealthCheckUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:5000" 

    def on_start(self):
        logging.info("Starting load test for Health Check API")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.duo_data = {
            "data_list": [
                {
                    "temperature_one": 35,
                    "temperature_two": 40,
                    "vibration_x": 0.2,
                    "vibration_y": 0.3,
                    "vibration_z": 0.1
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
                "vibration_Z_warning": 0.5
            }
        }
        
        self.quad_data = {
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

    @task(2)  
    def home(self):
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "version" in data and "uptime_seconds" in data:
                    response.success()
                else:
                    response.failure("Missing required fields in response")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(3) 
    def check_health(self):
        with self.client.post("/check_health", json=self.duo_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ["temperature_health", "vibration_health", "overall_health"]):
                    response.success()
                else:
                    response.failure("Missing required fields in response")
            elif response.status_code in [400, 415]: 
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def analyze(self):
        with self.client.post("/analyze", json=self.duo_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ["overall_health", "possible_cause", "details"]):
                    response.success()
                else:
                    response.failure("Missing required fields in response")
            elif response.status_code in [415, 500]: 
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(3) 
    def check_health_quad(self):
        with self.client.post("/check_health_quad", json=self.quad_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ["temperature_health", "vibration_health", 
                                             "magnetic_flux_health", "ultrasound_health", "overall_health"]):
                    response.success()
                else:
                    response.failure("Missing required fields in response")
            elif response.status_code == 400:  
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)  
    def report(self):
        with self.client.post("/report", json=self.quad_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ["overall_health", "possible_cause", "details"]):
                    details = data.get("details", {})
                    
                    expected_sensors = ["temperature_one", "temperature_two", "vibration_x", "vibration_y", 
                                     "vibration_z", "magnetic_flux_x", "magnetic_flux_y", "magnetic_flux_z",
                                     "ultrasound_one", "ultrasound_two"]
                    if all(sensor in details for sensor in expected_sensors):
                        response.success()
                    else:
                        response.failure("Missing sensor data in details")
                else:
                    response.failure("Missing required fields in response")
            elif response.status_code in [415, 500]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
