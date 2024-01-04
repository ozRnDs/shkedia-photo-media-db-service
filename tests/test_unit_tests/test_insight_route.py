import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from routes.insights import InsightServiceHandler, InsightEngine, InsightEngineBasic, InsightBasic, Insight, InsightEngineObjectEnum
from routes import search_utils

@pytest.fixture(scope="module")
def insight_handler_fixture(mock_db_service):
    insight_handler = InsightServiceHandler(db_service=mock_db_service,
                                            app_logging_service=None,
                                            auth_service=None)
    
    yield insight_handler

def test_put_insight_engine_nominal(insight_handler_fixture):
    # SETUP
    new_insight_engine = [InsightEngine(name="month",
                                           id="month_test",
                                           description="Month and year the media was created",
                                           input_source="input.images",
                                           input_queue_name="input.month",
                                           output_exchange_name="output.month"),
                            InsightEngine(name="object-v1", 
                                           description="Objects identified in the media",
                                           input_source="input.images",
                                           input_queue_name="input.yolov7",
                                           output_exchange_name="output.yolov7")]
    # RUN
    inserted_engines = insight_handler_fixture.put_insight_engine(new_insight_engine)
    # ASSERT
    assert len(inserted_engines) == len(new_insight_engine)
    for index, insight_engine in enumerate(inserted_engines):
        assert not insight_engine.id is None
        assert insight_engine.name == new_insight_engine[index].name

def test_put_insight_nominal(insight_handler_fixture):
    # SETUP
    new_insights = [Insight(insight_engine_id="month_test", 
                               media_id="id_for_test",
                               name="2023.08",
                               job_id="test_init_job_1"),
                    Insight(insight_engine_id="month_test", 
                               media_id="Doesn't Exists2",
                               name="2023.09",
                               job_id="test_init_job_2")]
    for i in range(10):
        new_insights.append(Insight(insight_engine_id="month_test", 
                               media_id=f"id_for_test_{i}",
                               name="2023.08",
                               job_id=f"test_job_{i}"))
    # RUN
    inserted_insights = insight_handler_fixture.put_insight(new_insights)
    # ASSERT
    assert len(inserted_insights) == len(new_insights)
    for index, insight_engine in enumerate(inserted_insights):
        assert not insight_engine.id is None
        assert insight_engine.name == new_insights[index].name

def test_get_insight_engine_mng_nominal(insight_handler_fixture):
    # SETUP
    insight_engine_id_to_find = "month_test"
    # RUN
    engine_data = insight_handler_fixture.get_engine_mng(engine_id=insight_engine_id_to_find)
    # ASSERT
    assert engine_data.name == "month"
    assert engine_data.input_source=="input.images"

def test_get_insight_engine_mng_not_found(insight_handler_fixture):
    # SETUP
    insight_engine_id_to_find = "month_test_dont"
    # RUN
    with pytest.raises(HTTPException) as err:
        engine_data = insight_handler_fixture.get_engine_mng(engine_id=insight_engine_id_to_find)
    # ASSERT
    assert err.value.status_code == 404

def test_get_all_engines_nominal(insight_handler_fixture):
    # SETUP
    # RUN
    engine_data = insight_handler_fixture.get_all_engines(response_type=InsightEngineObjectEnum.InsightEngineBasic)
    # ASSERT
    assert len(engine_data) > 0

def test_search_insight_by_name_nominal(insight_handler_fixture):
    """This test depends on all the tests in this test inorder to pass

    """    
    # SETUP
    search_condition_list = []

    new_request = MagicMock()
    new_request.query_params.multi_items.return_value=search_condition_list

    # RUN
    results01: search_utils.SearchResult = insight_handler_fixture.search_insight(new_request,search_field="name", search_value="2023.08")
    results02: search_utils.SearchResult = insight_handler_fixture.search_insight(new_request,search_field="name", search_value="2023.09")
    results03: search_utils.SearchResult = insight_handler_fixture.search_insight(new_request,search_field="name", search_value="2023.10")
    # ASSERT
    assert type(results01) == search_utils.SearchResult
    assert results01.total_results_number == 11
    assert results02.total_results_number == 1
    assert results03.total_results_number == 0