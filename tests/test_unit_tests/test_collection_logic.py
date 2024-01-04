import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from logics.collections import CollectionLogicService
from routes.collections import CollectionServiceHandler, CollectionBasic, CollectionPreview, CollectionObjectEnum
from routes import search_utils

@pytest.fixture(scope="module")
def collection_logic_fixture(mock_db_service) -> CollectionLogicService:
    collection_handler = CollectionLogicService(db_service=mock_db_service,
                                            app_logging_service=None,
                                            auth_service=None)
    
    yield collection_handler


def test_get_collections_metadata_by_names_nominal(collection_logic_fixture):
    # SETUP
    search_in_list = ["collection2","something_3"]
    # RUN
    results = collection_logic_fixture.get_collections_metadata_by_names(collections_names=search_in_list)
    # ASSERT
    assert len(results) == 6
    for _,result in results.items():
        assert type(result) == CollectionPreview
        assert result.name in search_in_list