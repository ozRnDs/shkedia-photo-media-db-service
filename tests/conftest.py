import logging
logger = logging.getLogger(__name__)
import sys, os
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from unittest.mock import MagicMock

import sqlalchemy

sys.path.append(f"{os.getcwd()}/src")
print(sys.path)

from main import app, app_config # TODO: Figure out better way to test the app
from models.media import MediaRequest
from db.sql_models import Base, User, DeviceOrm, MediaOrm, InsightEngineOrm, InsightOrm
from db.service import DBService

@pytest.fixture(scope="session")
def mock_db_service():
    mock_db_service = DBService(credential_file_location="/temp/postgres_credentials/postgres_credentials.json")
    mock_db_service.db_sql_engine = sqlalchemy.create_engine("sqlite://", echo=True)
    Base.metadata.drop_all(mock_db_service.db_sql_engine)
    Base.metadata.create_all(mock_db_service.db_sql_engine)
    
    list_of_items_to_insert = []

    new_user = User(user_name="test", password="test", user_id="test_user",
                    devices=[DeviceOrm(device_name="device1", device_id="test_device",
                                    media=[MediaOrm(media_name="media1", 
                                                media_type="IMAGE", 
                                                media_size_bytes=1024,
                                                device_media_uri="uri://test_uri",
                                                created_on=datetime(year=2023, month=8, day=25),
                                                owner_id="dontknow"),
                                            MediaOrm(media_name="media2", 
                                                media_type="IMAGE", 
                                                media_size_bytes=2048,
                                                device_media_uri="uri://test_uri_2",
                                                created_on=datetime(year=2023, month=8, day=20),
                                                owner_id="dontknow")]),
                            DeviceOrm(device_name="device2", device_id="test_device_2",
                                   media=[MediaOrm(media_name="media3", 
                                                media_type="IMAGE", 
                                                media_size_bytes=1024,
                                                device_media_uri="uri://test_uri",
                                                created_on=datetime(year=2023, month=8, day=10),
                                                owner_id="dontknow",
                                                media_id="id_for_test"),
                                            MediaOrm(media_name="media4", 
                                                media_type="IMAGE", 
                                                media_size_bytes=2048,
                                                device_media_uri="uri://test_uri_2",
                                                created_on=datetime(year=2023, month=10, day=25),
                                                owner_id="dontknow")])])
    
    list_of_items_to_insert.append(new_user)

    for i in range(4):
        list_of_items_to_insert.append(InsightEngineOrm(id=f"test_engine_{i}",
                                                        name=f"engine_{i}",
                                                        input_source="raw.images",
                                                        input_queue_name=f"input.engine_{i}",
                                                        output_exchange_name=f"output.engine_{i}"))
    for i in range(20):
        list_of_items_to_insert.append(MediaOrm(media_name=f"media_{i}", 
                                                media_type="IMAGE", 
                                                media_size_bytes=1024,
                                                device_media_uri=f"uri://test_uri_{i}",
                                                created_on=datetime(year=2023, month=8, day=10)+timedelta(days=i),
                                                owner_id="test",
                                                device_id="test_device_2",
                                                media_id=f"media_no_{i}"))
        if i%2==0:
            list_of_items_to_insert.append(InsightOrm(insight_engine_id=f"test_engine_{i%4}",
                                                      media_id=f"media_no_{i}",
                                                      name="devide_2"))
        if i%3==0:
            list_of_items_to_insert.append(InsightOrm(insight_engine_id=f"test_engine_{i%4}",
                                                      media_id=f"media_no_{i}",
                                                      name="something_3"))
    mock_db_service.insert(list_of_items_to_insert)

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