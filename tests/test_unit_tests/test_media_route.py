import pytest
from unittest.mock import MagicMock

from routes.media import MediaServiceHandler, MediaIDs, MediaThumbnail, MediaObjectEnum
from routes.search_utils import SearchResult
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, Request

@pytest.fixture(scope="module")
def media_handler_fixture(jwt_key_location_fixture, mock_db_service):
    media_handler = MediaServiceHandler(db_service=mock_db_service,
                                app_logging_service=None,
                                auth_service=None)
    yield media_handler

def test_search_media_nominal_mediaids(media_handler_fixture):
    # SETUP
    search_condition_list = []
    search_condition_list.append(("media_name","media3"))
    search_condition_list.append(("media_name","media1"))

    new_request = MagicMock()
    new_request.query_params.multi_items.return_value=search_condition_list

    # RUN
    results: SearchResult = media_handler_fixture.search_media(new_request)

    #
    assert not results is None
    assert type(results) == SearchResult
    assert results.total_results_number == 2
    assert len(results.results) == 2
    for media in results.results:
        assert type(media) is MediaIDs
        assert media.media_name in ["media3", "media1"]
        assert not "media_thumbnail" in media.model_fields

def test_search_media_nominal_mediathumbnail(media_handler_fixture):
    # SETUP
    search_condition_list = []
    search_condition_list.append(("media_name","media3"))
    search_condition_list.append(("media_name","media1"))

    new_request = MagicMock()
    new_request.query_params.multi_items.return_value=search_condition_list

    # RUN
    results: SearchResult = media_handler_fixture.search_media(new_request,response_type=MediaObjectEnum.MediaThumbnail)

    #
    assert not results is None
    assert type(results) == SearchResult
    assert results.total_results_number == 2
    assert len(results.results) == 2
    for media in results.results:
        assert type(media) is MediaThumbnail
        assert media.media_name in ["media3", "media1"]
        assert "media_thumbnail" in media.model_fields