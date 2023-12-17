import pytest
from unittest.mock import MagicMock

from routes.media import MediaServiceHandler
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, Request

@pytest.fixture(scope="module")
def media_handler_fixture(jwt_key_location_fixture, mock_db_service):
    media_handler = MediaServiceHandler(db_service=mock_db_service,
                                app_logging_service=None,
                                auth_service=None)
    yield media_handler

def test_search_media_nominal(media_handler_fixture):
    # SETUP
    search_condition_list = []
    search_condition_list.append(("media_name","media3"))
    search_condition_list.append(("media_name","media1"))

    new_request = MagicMock()
    new_request.query_params.multi_items.return_value=search_condition_list

    # RUN
    results = media_handler_fixture.search_media(new_request)

    # ASSERT
    