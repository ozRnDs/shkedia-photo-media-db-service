import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from logics.collections import CollectionLogicService
from routes.collections import CollectionServiceHandler, CollectionBasic, CollectionPreview, CollectionObjectEnum
from routes import search_utils

@pytest.fixture(scope="module")
def collection_handler_fixture(mock_db_service):

    mock_auth_service = MagicMock()

    collection_logics = CollectionLogicService(db_service=mock_db_service,
                                              app_logging_service=None,
                                              auth_service=mock_auth_service)
    collection_handler = CollectionServiceHandler(db_service=mock_db_service,
                                            app_logging_service=None,
                                            auth_service=mock_auth_service,
                                            collection_logics=collection_logics)
    
    yield collection_handler

def test_get_collections_list_nominal(collection_handler_fixture):
    # SETUP
    
    # RUN
    results = collection_handler_fixture.get_collections_list()
    # ASSERT
    assert len(results) == 6
    for result in results:
        assert type(result) == CollectionBasic

def test_get_collection_nominal(collection_handler_fixture):
    # SETUP
    
    # RUN
    results = collection_handler_fixture.get_collection_by_name(collection_name="collection2")
    # ASSERT
    assert len(results.results) == 10
    for result in results.results:
        assert type(result) == CollectionPreview