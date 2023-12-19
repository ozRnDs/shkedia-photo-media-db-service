import logging
logger = logging.getLogger(__name__)
import sys, os
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from unittest.mock import MagicMock

import sqlalchemy

sys.path.append(f"{os.getcwd()}/src")
print(sys.path)

from main import app, app_config # TODO: Figure out better way to test the app
from models.media import MediaRequest
from db.sql_models import Base, User, Device, Media
from db.service import DBService

@pytest.fixture(scope="session")
def mock_db_service():
    mock_db_service = DBService(credential_file_location="/temp/postgres_credentials/postgres_credentials.json")
    mock_db_service.db_sql_engine = sqlalchemy.create_engine("sqlite://", echo=True)
    Base.metadata.drop_all(mock_db_service.db_sql_engine)
    Base.metadata.create_all(mock_db_service.db_sql_engine)
    
    new_user = User(user_name="test", password="test", 
                    devices=[Device(device_name="device1", 
                                    media=[Media(media_name="media1", 
                                                media_type="IMAGE", 
                                                media_size_bytes=1024,
                                                device_media_uri="uri://test_uri",
                                                created_on=datetime(year=2023, month=8, day=25),
                                                owner_id="dontknow"),
                                            Media(media_name="media2", 
                                                media_type="IMAGE", 
                                                media_size_bytes=2048,
                                                device_media_uri="uri://test_uri_2",
                                                created_on=datetime(year=2023, month=8, day=20),
                                                owner_id="dontknow")]),
                            Device(device_name="device2",
                                   media=[Media(media_name="media3", 
                                                media_type="IMAGE", 
                                                media_size_bytes=1024,
                                                device_media_uri="uri://test_uri",
                                                created_on=datetime(year=2023, month=8, day=10),
                                                owner_id="dontknow"),
                                            Media(media_name="media4", 
                                                media_type="IMAGE", 
                                                media_size_bytes=2048,
                                                device_media_uri="uri://test_uri_2",
                                                created_on=datetime(year=2023, month=10, day=25),
                                                owner_id="dontknow")])])

    mock_db_service.insert([new_user])

    yield mock_db_service

@pytest.fixture(scope="session")
def jwt_key_location_fixture():
    return "/temp/jwt_token"

@pytest.fixture(scope="session")
def client_fixture(jwt_key_location_fixture):
    app_config.AUTH_DB_CREDENTIALS_LOCATION="/temp/postgres_credentials/postgres_credentials.json"
    app_config.JWT_KEY_LOCATION=jwt_key_location_fixture
    app_config.TOKEN_TIME_PERIOD=1
    client = TestClient(app)

    yield client

    client.close()

@pytest.fixture(scope="session")
def media_request_fixture_device_doesnt_exist():
    test_media = MediaRequest(media_name="Test_Media",
                            media_size_bytes=1024,
                            media_thumbnail="NoImage",
                            media_type="IMAGE",
                            created_on=datetime.now().isoformat(),
                            device_id="NotExist",
                            device_media_uri="uri://something")
    
    yield test_media

@pytest.fixture(scope="session")
def media_request_fixture_nominal():
    test_media = MediaRequest(media_name="Test_Media",
                            media_size_bytes=1024,
                            media_thumbnail="NoImage",
                            media_type="IMAGE",
                            created_on=datetime.now().isoformat(),
                            device_id="9b67e6b5-e8e8-468a-8b52-c9f8468605df",
                            device_media_uri="uri://something")
    
    yield test_media