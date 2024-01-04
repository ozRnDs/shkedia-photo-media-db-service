import pytest
from unittest.mock import MagicMock

from routes.media import MediaServiceHandler, MediaIDs, MediaThumbnail, MediaObjectEnum, MediaMetadata, MediaDB, MediaRequest
from routes.search_utils import SearchResult
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, Request
from datetime import datetime

@pytest.fixture(scope="module")
def media_handler_fixture(jwt_key_location_fixture, mock_db_service):
    media_handler = MediaServiceHandler(db_service=mock_db_service,
                                app_logging_service=None,
                                auth_service=MagicMock())
    yield media_handler

@pytest.fixture(scope="module")
def request_fixture():
    new_request = MagicMock()
    new_request.user_data.id = "dontknow"
    return new_request

def test_search_media_nominal_mediaids(media_handler_fixture, request_fixture):
    # SETUP
    search_condition_list = []
    search_condition_list.append(("media_name","media3"))
    search_condition_list.append(("media_name","media1"))

    request_fixture.query_params.multi_items.return_value=search_condition_list

    # RUN
    results: SearchResult = media_handler_fixture.search_media(request_fixture)

    #
    assert not results is None
    assert type(results) == SearchResult
    assert results.total_results_number == 2
    assert len(results.results) == 2
    for media in results.results:
        assert type(media) is MediaIDs
        assert media.media_name in ["media3", "media1"]
        assert not "media_thumbnail" in media.model_fields

def test_search_media_nominal_mediathumbnail(media_handler_fixture,request_fixture):
    # SETUP
    search_condition_list = []
    search_condition_list.append(("media_name","media3"))
    search_condition_list.append(("media_name","media1"))

    request_fixture.query_params.multi_items.return_value=search_condition_list

    # RUN
    results: SearchResult = media_handler_fixture.search_media(request_fixture,response_type=MediaObjectEnum.MediaThumbnail)

    #
    assert not results is None
    assert type(results) == SearchResult
    assert results.total_results_number == 2
    assert len(results.results) == 2
    for media in results.results:
        assert type(media) is MediaThumbnail
        assert media.media_name in ["media3", "media1"]
        assert "media_thumbnail" in media.model_fields

def test_get_media_not_existing(media_handler_fixture,request_fixture):
    # SETUP
    media_id = "Doesn't Exist"

    # RUN
    with pytest.raises(HTTPException) as err:
        media = media_handler_fixture.get_media(request_fixture, media_id=media_id, response_type=MediaObjectEnum.MediaMetadata)

    # ASSERT
    assert err.value.status_code == 404
    assert "was not found" in err.value.detail

def test_get_media_nominal(media_handler_fixture,request_fixture):
    # SETUP
    media_id = "id_for_test"

    # RUN
    media = media_handler_fixture.get_media(request_fixture, media_id=media_id, response_type=MediaObjectEnum.MediaMetadata)

    # ASSERT
    assert type(media) == MediaMetadata

def test_update_media_nominal(media_handler_fixture,request_fixture):
    # SETUP
    get_media_before: MediaMetadata = media_handler_fixture.get_media(request_fixture,media_id="id_for_test", response_type=MediaObjectEnum.MediaMetadata)
    old_description = get_media_before.media_description

    new_object_values = MediaDB(media_id="id_for_test", media_description="The is updated media", 
                                created_on=datetime.now(), device_id="test", device_media_uri="uri://test_uri", 
                                owner_id="dontknow", media_type="IMAGE", media_size_bytes=1024, media_name="media3", media_width=800, media_height=800)
    # RUN
    result = media_handler_fixture.update_media(request_fixture,new_object_values)
    # Assert
    assert result.media_id == new_object_values.media_id
    get_media: MediaMetadata = media_handler_fixture.get_media(request_fixture,media_id="id_for_test", response_type=MediaObjectEnum.MediaMetadata)
    assert get_media.media_description == new_object_values.media_description
    assert get_media.media_description != old_description
    assert get_media.media_width == 800
    assert get_media.media_height == 800

def test_put_media_nominal(media_handler_fixture,request_fixture):
    # SETUP
    new_media = [MediaRequest(media_name="Test Media", media_type="IMAGE", media_size_bytes=1024,
                            created_on=datetime(year=1955,month=12,day=3,hour=13,minute=20),
                            device_id="test_device",device_media_uri="/this/is/test/1"),
                MediaRequest(media_name="Test Media2", media_type="IMAGE", media_size_bytes=1024,
                            created_on=datetime(year=1955,month=12,day=3,hour=13,minute=21),
                            device_id="test_device",device_media_uri="/this/is/test/2"),
                MediaRequest(media_name="Test Media3", media_type="IMAGE", media_size_bytes=1024,
                            created_on=datetime(year=1955,month=12,day=3,hour=13,minute=21),
                            device_id="test_device_2",device_media_uri="/this/is/test/2")
                            ]
    
    # RUN
    updated_media = media_handler_fixture.put_media(request_fixture,new_media)

    # ASSERT
    assert len(updated_media) == len(new_media)
    for index, media in enumerate(updated_media):
        assert media.owner_id == "dontknow"
        assert not media.media_id is None
        assert media.media_name == new_media[index].media_name
        assert media.created_on == new_media[index].created_on
