import sys

from fastapi import FastAPI

import traceback

from config import app_config
from authentication.service import AuthService
from db.service import DBService

from routes.media import MediaServiceHandler

from db.sqlalchemy_models import Base

# from models.user import UserDB
# from models.device import Device
# from models.session import Session
# from models.media import MediaDB
    
app = FastAPI(description="Rest API Interface for the media db service")

#TODO: Bind auth service as middleware to all requests

# Initialize all app services
try:
    db_service = DBService(credential_file_location=app_config.AUTH_DB_CREDENTIALS_LOCATION, environment=app_config.ENVIRONMENT, debug=app_config.DEBUG)
    db_service.create_tables(Base)

except Exception as err:
    app_config.logger.error(f"Failed to initialize the db. {err}")
try:
    auth_service = AuthService(jwt_key_location=app_config.JWT_KEY_LOCATION,
                               db_service=db_service,
                               default_expire_delta_min=app_config.TOKEN_TIME_PERIOD)
    media_service = MediaServiceHandler(db_service=db_service, app_logging_service=None, auth_service=auth_service)
except Exception as err:
    app_config.logger.error(f"Failed to start service. {err}")
    traceback.print_exc()


# Connect all routes
# Example: app.include_router(new_component.router, prefix="/path")

app.include_router(media_service.router, prefix="/v1/media")