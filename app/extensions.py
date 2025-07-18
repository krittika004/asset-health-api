from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/apidocs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.yaml'  # Our API url (can be a local file)

# Call factory function to create our blueprint
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Asset Health Prediction API"
    }
)
