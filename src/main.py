import sys

from fastapi import FastAPI

import traceback

from config import app_config
from authentication.service import AuthService
from db.service import DBService
from db.user_service import UserDBService

from routes.media import MediaServiceHandler
from routes.insights import InsightServiceHandler
from routes.insights_v3 import InsightServiceHandlerV3
from routes.collections import CollectionServiceHandler
from routes.jobs import JobsServiceHandler
from logics.collections import CollectionLogicService

# from models.user import UserDB
# from models.device import Device
# from models.session import Session
# from models.media import MediaDB
    
app = FastAPI(description="Rest API Interface for the media db service")

#TODO: Bind auth service as middleware to all requests

# Initialize all app services
try:
    db_service = DBService(credential_file_location=app_config.AUTH_DB_CREDENTIALS_LOCATION, environment=app_config.ENVIRONMENT, debug=app_config.DEBUG)
    user_db_service = UserDBService(host=app_config.USER_DB_HOST, port=app_config.USER_DB_PORT)
    # db_service.create_tables(Base)

except Exception as err:
    app_config.logger.error(f"Failed to initialize the db. {err}")
try:
    auth_service = AuthService(jwt_key_location=app_config.JWT_KEY_LOCATION,
                               user_db_service=user_db_service,
                               default_expire_delta_min=app_config.TOKEN_TIME_PERIOD)
    media_service = MediaServiceHandler(db_service=db_service, app_logging_service=None, auth_service=auth_service)
    insight_service = InsightServiceHandler(db_service=db_service, app_logging_service=None, auth_service=auth_service)
    insight_service_v3 = InsightServiceHandlerV3(db_service=db_service, app_logging_service=None, auth_service=auth_service)
    collection_logics = CollectionLogicService(db_service=db_service, app_logging_service=None, auth_service=auth_service)
    collection_service = CollectionServiceHandler(db_service=db_service, app_logging_service=None, auth_service=auth_service, collection_logics=collection_logics)
    jobs_service = JobsServiceHandler(db_service=db_service,app_logging_service=None, auth_service=auth_service)
except Exception as err:
    app_config.logger.error(f"Failed to start service. {err}")
    traceback.print_exc()
    sys.exit(1)

# Connect all routes
# Example: app.include_router(new_component.router, prefix="/path")

app.include_router(media_service.router, prefix="/v1/media")
app.include_router(insight_service.router, prefix="/v2/insights")
app.include_router(insight_service_v3.router, prefix="/v3")
app.include_router(collection_service.router, prefix="/v2")
app.include_router(jobs_service.router,prefix="/v2")
app.include_router(auth_service.router,prefix="")