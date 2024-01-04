import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from project_shkedia_models.media import MediaRequest, MediaDB, MediaDeviceStatus, MediaUploadStatus
from routes.search_utils import SearchResult

def test_put_media_device_doent_exists(client_fixture: TestClient):
    # SETUP
    test_media = [MediaRequest(media_name="Test_Media",
                              media_size_bytes=1024,
                              media_thumbnail="NoImage",
                              media_type="IMAGE",
                              created_on=datetime.now(),
                              device_id="NotExist",
                              device_media_uri="uri://something").model_dump()]


    # Test
    response = client_fixture.put("/v1/media", json=test_media)

    # ASSERT
    assert response.status_code == 400
    assert "not exists" in response.json()["detail"]

def test_put_media_nominal(client_fixture: TestClient, media_request_fixture_nominal):
    # SETUP
    source_device = {
                        "device_id": "9b67e6b5-e8e8-468a-8b52-c9f8468605df",
                        "device_name": "test_device",
                        "owner_id": "3b90bdf8-efe4-403b-93d2-9e1aa83e5413",
                        "created_on": "2023-11-29T11:55:16.275878",
                        "status": "ACTIVE"
                    }

    test_media = media_request_fixture_nominal
    # Test
    response = client_fixture.put("/v1/media", content=test_media.model_dump_json())

    # ASSERT
    assert response.status_code == 200
    response_model = MediaDB(**response.json())

    for field_name, field_value in test_media.model_dump().items():
        assert response_model.model_dump()[field_name] == field_value
    response_model.media_status_on_device == MediaDeviceStatus.EXISTS
    response_model.upload_status == MediaUploadStatus.PENDING
    response_model.owner_id == source_device["owner_id"]

def test_get_search_media_nominal(client_fixture, media_request_fixture_device_doesnt_exist):
    
    # SETUP

    search_field = "media_name"
    search_value = "Test_Media"

    # Test
    response = client_fixture.get(f"/v1/media/search?search_field={search_field}&search_value={search_value}")

    # ASSERT
    assert response.status_code == 200
    response_json = response.json()
    if "total_result_number" in response_json:
        temp_media_object = SearchResult(**response_json)
    if "media_id" in response_json:
        temp_media_object = MediaDB(**response_json)