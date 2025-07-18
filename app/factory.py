from flask import Flask
from flasgger import Swagger
import os
from .routes.api_routes import register_routes

def create_app():
    app = Flask(__name__)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "title": "Asset Health Prediction API",
        "description": "API for predicting asset health using various sensors",
        "termsOfService": "",
        "uiversion": 2
    }

    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    swagger_file = os.path.join(base_dir, 'swagger', 'swagger.yaml')
    Swagger(app, 
           template_file=swagger_file,
           config=swagger_config)

    register_routes(app)
    return app
