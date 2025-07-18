from flask import request, jsonify
import numpy as np
import warnings
import logging
from datetime import datetime, timezone
from app.health_utils import (
    analyze_sensor_data_duo, analyze_sensor_data_quad,
    field_alias_duo, field_alias
)

start_time = datetime.now(timezone.utc)

warnings.filterwarnings("ignore")
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)
start_time = datetime.now(timezone.utc)
def register_routes(app):
    @app.route('/', methods=['GET'])
    def home():
        current_time = datetime.now(timezone.utc)
        uptime_duration = current_time - start_time
        uptime_seconds = int(uptime_duration.total_seconds())

        return jsonify({
            "status": "success",
            "message": "Welcome to the Production Prediction API",
            "version": "3.0.0",
            "uptime_seconds": uptime_seconds
        }), 200

    @app.route('/check_health', methods=['POST'])
    def check_health():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid or missing JSON in request"}), 400
            
            data_list = data.get("data_list")
            thresholds = data.get("thresholds")

            if data_list is None or thresholds is None:
                return jsonify({"error": "Missing 'data_list' or 'thresholds' in request"}), 400

            if not isinstance(data_list, list) or not data_list:
                return jsonify({"error": "Missing 'data_list' or 'thresholds' in request"}), 400

            if not isinstance(data_list[0], dict) or "temperature_one" not in data_list[0]:
                return jsonify({"error": "Missing required field: 'temperature_one'"}), 400

            health_status = {
                "temperature_skin": [],
                "temperature_bearing": [],
                "vibration_x": [],
                "vibration_y": [],
                "vibration_z": []
            }

            try:
                temperature_skin_values = [entry["temperature_one"] for entry in data_list]
                temperature_bearing_values = [entry["temperature_two"] for entry in data_list]
              
                vibration_x_values = [entry["vibration_x"] for entry in data_list]
                vibration_y_values = [entry["vibration_y"] for entry in data_list]
                vibration_z_values = [entry["vibration_z"] for entry in data_list]
                
                if not all([temperature_skin_values, temperature_bearing_values,
                           vibration_x_values, vibration_y_values, vibration_z_values]):
                    return jsonify({"error": "Empty data list or missing sensor values"}), 400

                mean_temperature_skin = sum(temperature_skin_values) / len(temperature_skin_values)
                mean_temperature_bearing = sum(temperature_bearing_values) / len(temperature_bearing_values)
                mean_vibration_x = sum(vibration_x_values) / len(vibration_x_values)
                mean_vibration_y = sum(vibration_y_values) / len(vibration_y_values)
                mean_vibration_z = sum(vibration_z_values) / len(vibration_z_values)

                health_status["temperature_skin"].append(
                    "healthy" if thresholds.get("temperature_skin_healthy", float('-inf')) <= mean_temperature_skin <= thresholds.get("temperature_skin_warning", float('inf'))
                    else "unhealthy"
                )
                health_status["temperature_bearing"].append(
                    "healthy" if thresholds.get("temperature_bearing_healthy", float('-inf')) <= mean_temperature_bearing <= thresholds.get("temperature_bearing_warning", float('inf'))
                    else "unhealthy"
                )
                health_status["vibration_x"].append(
                    "healthy" if thresholds.get("vibration_X_healthy", float('-inf')) <= mean_vibration_x <= thresholds.get("vibration_X_warning", float('inf'))
                    else "unhealthy"
                )
                health_status["vibration_y"].append(
                    "healthy" if thresholds.get("vibration_Y_healthy", float('-inf')) <= mean_vibration_y <= thresholds.get("vibration_Y_warning", float('inf'))
                    else "unhealthy"
                )
                health_status["vibration_z"].append(
                    "healthy" if thresholds.get("vibration_Z_healthy", float('-inf')) <= mean_vibration_z <= thresholds.get("vibration_Z_warning", float('inf'))
                    else "unhealthy"
                )
                temperature_health = "healthy" if "unhealthy" not in health_status["temperature_skin"] + health_status["temperature_bearing"] else "unhealthy"
                vibration_health = "healthy" if "unhealthy" not in health_status["vibration_x"] + health_status["vibration_y"] + health_status["vibration_z"] else "unhealthy"
                overall_health = "Healthy" if temperature_health == "healthy" and vibration_health == "healthy" else "Unhealthy"
                
                return jsonify({
                    "temperature_health": temperature_health,
                    "vibration_health": vibration_health,
                    "overall_health": overall_health
                })
                
            except KeyError as e:
                return jsonify({"error": f"Missing required field: {str(e)}"}), 400
            except ZeroDivisionError:
                return jsonify({"error": "Empty data list or missing sensor values"}), 400
            except Exception as e:
                return jsonify({"error": f"An error occurred while processing the request: {str(e)}"}), 500
                
        except Exception as e:
            return jsonify({"error": "Invalid or missing JSON in request"}), 400
            
    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Unsupported Media Type"}), 415
                
            data_list = data.get("data_list", [])
            thresholds = data.get("thresholds", {})
            
            if not data_list or not thresholds:
                return jsonify({"error": "Missing 'data_list' or 'thresholds' in request"}), 500
            
            try:
                overall_status, possible_cause, details = analyze_sensor_data_duo(
                    data_list, thresholds, field_alias_duo
                )
                overall_health = "Healthy" if overall_status == "MACHINE IS IN GOOD CONDITION" else "Unhealthy"
                return jsonify({
                    "overall_health": overall_health,
                    "possible_cause": possible_cause,
                    "details": details
                })
            except Exception:
                return jsonify({"error": "Failed to analyze sensor data"}), 500
        except Exception:
            return jsonify({"error": "Unsupported Media Type"}), 415

    @app.route('/check_health_quad', methods=['POST'])
    def check_health_quad():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Invalid or missing JSON in request"}), 400
            
            data_list = data.get("data_list", [])
            thresholds = data.get("thresholds", {})
        except Exception:
            return jsonify({"error": "Invalid or missing JSON in request"}), 400
        if not data_list or not thresholds:
            return jsonify({"error": "Missing 'data_list' or 'thresholds' in request"}), 400
        health_status = {
            "temperature_skin"   : [],
            "temperature_bearing": [],
            "vibration_x"        : [],
            "vibration_y"        : [],
            "vibration_z"        : [],
            "magnetic_flux_x"    : [],
            "magnetic_flux_y"    : [],
            "magnetic_flux_z"    : [],
            "ultrasound_one"     : [],
            "ultrasound_two"     : []
        }
        t = thresholds
        skin_vals     = [row["temperature_one"] for row in data_list]
        bearing_vals  = [row["temperature_two"] for row in data_list]
        mean_skin     = sum(skin_vals)    / len(skin_vals)
        mean_bearing  = sum(bearing_vals) / len(bearing_vals)
        health_status["temperature_skin"].append(
            "healthy" if t["temperature_skin_healthy"] <= mean_skin <= t["temperature_skin_warning"]
            else "unhealthy"
        )
        health_status["temperature_bearing"].append(
            "healthy" if t["temperature_bearing_healthy"] <= mean_bearing <= t["temperature_bearing_warning"]
            else "unhealthy"
        )
        vib_x_vals, vib_y_vals, vib_z_vals = [], [], []
        for row in data_list:
            vib_x_vals.append(row["vibration_x"])
            vib_y_vals.append(row["vibration_y"])
            vib_z_vals.append(row["vibration_z"])
        mean_vx = sum(vib_x_vals) / len(vib_x_vals)
        mean_vy = sum(vib_y_vals) / len(vib_y_vals)
        mean_vz = sum(vib_z_vals) / len(vib_z_vals)
        health_status["vibration_x"].append(
            "healthy" if t["vibration_X_healthy"] <= mean_vx <= t["vibration_X_warning"]
            else "unhealthy"
        )
        health_status["vibration_y"].append(
            "healthy" if t["vibration_Y_healthy"] <= mean_vy <= t["vibration_Y_warning"]
            else "unhealthy"
        )
        health_status["vibration_z"].append(
            "healthy" if t["vibration_Z_healthy"] <= mean_vz <= t["vibration_Z_warning"]
            else "unhealthy"
        )
        flux_x_vals, flux_y_vals, flux_z_vals = [], [], []
        for row in data_list:
            flux_x_vals.append(row["magnetic_flux_x"])
            flux_y_vals.append(row["magnetic_flux_y"])
            flux_z_vals.append(row["magnetic_flux_z"])
        mean_fx = sum(flux_x_vals) / len(flux_x_vals)
        mean_fy = sum(flux_y_vals) / len(flux_y_vals)
        mean_fz = sum(flux_z_vals) / len(flux_z_vals)
        health_status["magnetic_flux_x"].append(
            "healthy" if t["magnetic_flux_X_healthy"] <= mean_fx <= t["magnetic_flux_X_warning"]
            else "unhealthy"
        )
        health_status["magnetic_flux_y"].append(
            "healthy" if t["magnetic_flux_Y_healthy"] <= mean_fy <= t["magnetic_flux_Y_warning"]
            else "unhealthy"
        )
        health_status["magnetic_flux_z"].append(
            "healthy" if t["magnetic_flux_Z_healthy"] <= mean_fz <= t["magnetic_flux_Z_warning"]
            else "unhealthy"
        )
        us1_vals, us2_vals = [], []
        for row in data_list:
            us1_vals.append(row["ultrasound_one"])
            us2_vals.append(row["ultrasound_two"])
        mean_us1 = sum(us1_vals) / len(us1_vals)
        mean_us2 = sum(us2_vals) / len(us2_vals)
        health_status["ultrasound_one"].append(
            "healthy" if t["ultrasound_one_healthy"] <= mean_us1 <= t["ultrasound_one_warning"]
            else "unhealthy"
        )
        health_status["ultrasound_two"].append(
            "healthy" if t["ultrasound_two_healthy"] <= mean_us2 <= t["ultrasound_two_warning"]
            else "unhealthy"
        )
        temperature_health = (
            "healthy" if "unhealthy" not in health_status["temperature_skin"] + health_status["temperature_bearing"]
            else "unhealthy"
        )
        vibration_health = (
            "healthy" if "unhealthy" not in health_status["vibration_x"] + health_status["vibration_y"] + health_status["vibration_z"]
            else "unhealthy"
        )
        flux_health = (
            "healthy" if "unhealthy" not in health_status["magnetic_flux_x"] + health_status["magnetic_flux_y"] + health_status["magnetic_flux_z"]
            else "unhealthy"
        )
        ultrasound_health = (
            "healthy" if "unhealthy" not in health_status["ultrasound_one"] + health_status["ultrasound_two"]
            else "unhealthy"
        )
        overall_health = (
            "Healthy" if all(h == "healthy" for h in [temperature_health, vibration_health, flux_health, ultrasound_health])
            else "Unhealthy"
        )
        return jsonify({
            "temperature_health": temperature_health,
            "vibration_health" : vibration_health,
            "magnetic_flux_health": flux_health,
            "ultrasound_health" : ultrasound_health,
            "overall_health"    : overall_health
        })

    @app.route('/report', methods=['POST'])
    def report():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({"error": "Unsupported Media Type"}), 415

            data_list = data.get("data_list", [])
            thresholds = data.get("thresholds", {})
            if not data_list or not thresholds:
                return jsonify({"error": "Missing 'data_list' or 'thresholds' in request"}), 500
                
            try:
                overall_status, possible_cause, details = analyze_sensor_data_quad(
                    data_list, thresholds, field_alias
                )
                overall_health = "Healthy" if overall_status == "MACHINE IS IN GOOD CONDITION" else "Unhealthy"
                
                return jsonify({
                    "overall_health": overall_health,
                    "possible_cause": possible_cause,
                    "details": details
                })
            except Exception:
                return jsonify({"error": "Failed to analyze sensor data"}), 500
        except Exception:
            return jsonify({"error": "Unsupported Media Type"}), 415 