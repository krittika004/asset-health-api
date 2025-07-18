# Asset Health Prediction API

A Flask-based API for asset health prediction using sensor data. The API provides endpoints for health checks and detailed analysis of temperature, vibration, magnetic flux, and ultrasound sensor data.

## Project Structure

```
Asset-Health-Prediction/
│
├── app/
│   ├── __init__.py         # App factory and route registration
│   ├── routes.py           # All Flask API endpoints
│   ├── health_utils.py     # Health analysis and utility functions
│   └── config.py           # App configuration
│
├── wsgi.py                 # WSGI entry point for production
├── app.py                  # Development entry point
├── requirements.txt        # Python dependencies
├── Procfile                # For deployment (e.g., Heroku)
├── Readme.md               # Project documentation
```

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Asset-Health-Prediction
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

### Development

```bash
python app.py
```

- The API will be available at `http://127.0.0.1:5000/`

### Production (Gunicorn/Heroku)

```bash
gunicorn wsgi:app
```

- The app will be served using the WSGI entry point.
- The `Procfile` is set up for Heroku deployment.

## API Endpoints

- `GET /` — Welcome message
- `POST /check_health` — Basic health check for temperature and vibration
- `POST /analyze` — Detailed health analysis (duo sensors)
- `POST /check_health_quad` — Health check for temperature, vibration, magnetic flux, and ultrasound
- `POST /report` — Detailed health analysis (quad sensors)

### Example Request (POST /check_health)

```json
{
  "data_list": [
    {
      "temperature_one": 35,
      "temperature_two": 40,
      "vibration_x": 0.2,
      "vibration_y": 0.3,
      "vibration_z": 0.1
    }
  ],
  "thresholds": 
    {
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
```

### Example Response

```json
{
  "temperature_health": "healthy",
  "vibration_health": "healthy",
  "overall_health": "Healthy"
}
```

## Notes

- All endpoints expect and return JSON.
- For production, use Gunicorn or a similar WSGI server.
- For local development, use `python app.py`.

## License

MIT
