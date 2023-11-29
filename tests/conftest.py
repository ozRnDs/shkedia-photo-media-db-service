import logging
logger = logging.getLogger(__name__)
import sys, os
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

sys.path.append(f"{os.getcwd()}/src")
print(sys.path)

from main import app, app_config # TODO: Figure out better way to test the app
from models.media import MediaRequest

@pytest.fixture(scope="session")
def client_fixture():
    app_config.AUTH_DB_CREDENTIALS_LOCATION="/temp/postgres_credentials/postgres_credentials.json"
    app_config.JWT_KEY_LOCATION="/temp/jwt_token"
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