import traceback
import sys
import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import Union, List, Annotated
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session
from enum import Enum


from db.sql_models import InsightEngineOrm, InsightOrm
from project_shkedia_models.insights import InsightEngineBasic,InsightEngine,InsightBasic, Insight, InsightEngineObjectEnum, InsightObjectEnum, InsightEngineValues
from db.service import DBService
from authentication.service import AuthService
from project_shkedia_models.parser import sql_model_to_pydantic_model
from . import search_utils

class InsightServiceHandlerV3:
    def __init__(self, 
                 db_service: DBService,
                 app_logging_service,
                 auth_service: AuthService
                 ):
        self.db_service = db_service
        self.logging_service = app_logging_service
        self.auth_service = auth_service
        if not self.db_service.is_ready():
            raise Exception("Can't initializes without db_service")
        self.router = self.__initialize_routes__()


    def __initialize_routes__(self):
        router = APIRouter(tags=["insights-v3"],
                        #    dependencies=[Depends(self.auth_service.__get_user_from_token__)],
                           )
        router.add_api_route(path="/insights-engines", 
                             endpoint=self.put_insight_engine,
                             methods=["put"],
                             response_model=List[InsightEngineBasic])
        router.add_api_route(path="/insights-engines",
                             endpoint=self.update_insight_engine,
                             methods=["post"],
                             response_model=InsightEngineBasic
                             )
        router.add_api_route(path="/insights-engines/mng/{engine_id}",
                             endpoint=self.get_engine,
                             methods=["get"],
                             response_model=Union[InsightEngine, InsightEngineBasic])
        router.add_api_route(path="/insights-engines",
                             endpoint=self.get_all_engines,
                             methods=["get"],
                             response_model=Union[List[InsightEngineBasic],List[InsightEngineValues]])
        router.add_api_route(path="/insights-engines/search",
                             endpoint=self.search_engine,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="/insights-engines/{engine_id}",
                             endpoint=self.get_engine,
                             methods=["get"],
                             response_model=Union[InsightEngineBasic, InsightEngineValues])
        router.add_api_route(path="/insights",
                             endpoint=self.put_insight,
                             methods=["put"],
                             response_model=List[InsightBasic])
        router.add_api_route(path="/insights/search",
                             endpoint=self.search_insight,
                             methods=["get"],
                             response_model=search_utils.SearchResult,
                             dependencies=[Depends(self.auth_service.auth_request)])
        return router


    def put_insight_engine(self, insight_engine_list: List[InsightEngine]) -> List[InsightEngineBasic]:
        try:
            insight_engine_orm_list = [InsightEngineOrm(**insight_engine.model_dump()) for insight_engine in insight_engine_list]
            if self.db_service.insert(insight_engine_orm_list):
                return [InsightEngineBasic(**insight_engine.__dict__) for insight_engine in insight_engine_list]
            raise HTTPException(status_code=500, detail="Couldn't insert insight engines")
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create engines")

    def put_insight(self, insight_list: List[Insight]) -> List[InsightBasic]:
        try:
            insights_orm_list = [InsightOrm(**insight.model_dump()) for insight in insight_list]
            if self.db_service.insert(insights_orm_list):
                return [InsightBasic(**insight.__dict__) for insight in insights_orm_list]
            raise HTTPException(status_code=500, detail="Couldn't insert insight engines")
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create engines")
        pass

    def get_engine_mng(self, engine_id: str = None, response_type: InsightEngineObjectEnum = InsightEngineObjectEnum.InsightEngine):
        try:
            response_type = getattr(sys.modules["project_shkedia_models.insights"], response_type.value)
            find_media = self.db_service.select(InsightEngineOrm, response_type, id=[engine_id])
            if find_media is None or len(find_media)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight engine was not found")
            return find_media[0]
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Server Internal Error")

    def get_all_engines(self, response_type: InsightEngineObjectEnum = InsightEngineObjectEnum.InsightEngineBasic):
        try:
            response_type = getattr(sys.modules["project_shkedia_models.insights"], response_type.value)
            engine_results = self.db_service.select(InsightEngineOrm, output_model=response_type)
            if engine_results is None or len(engine_results)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight engine was not found")           
            if response_type == InsightEngineValues:
                for engine in engine_results:
                    engine: InsightEngineValues = engine
                    class InsightsNames(BaseModel):
                        name: str
                    insights_results: List[InsightsNames] = self.db_service.select(InsightOrm,
                                                                                   output_model=InsightsNames,
                                                                                   distinct=InsightOrm.name,
                                                                                   order_by=InsightOrm.name,
                                                                                   insight_engine_id=[engine.id])
                    engine.insights_names = [item.name for item in insights_results]
            return engine_results
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            traceback.print_exc()
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Server Internal Error")

    def get_engine(self, engine_id: str = None, response_type: InsightEngineObjectEnum = InsightEngineObjectEnum.InsightEngineBasic):
        try:
            response_type = getattr(sys.modules["project_shkedia_models.insights"], response_type.value)
            if engine_id:
                engine_results = self.db_service.select(InsightEngineOrm, output_model=response_type, id=[engine_id])
            else:
                engine_results = self.db_service.select(InsightEngineOrm, output_model=response_type)
            if engine_results is None or len(engine_results)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight engine was not found")
            engine_results = engine_results[0]
            if response_type == InsightEngineValues:
                engine_results: InsightEngineValues = engine_results
                class InsightsNames(BaseModel):
                    name: str
                insights_results: List[InsightsNames] = self.db_service.select(InsightOrm,output_model=InsightsNames,distinct=InsightOrm.name,order_by=InsightOrm.name,insight_engine_id=[engine_results.id])
                engine_results.insights_names = [item.name for item in insights_results]
            return engine_results
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Server Internal Error")

    def search_engine(self, request: Request, search_field: str = "name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0, response_type: InsightEngineObjectEnum=InsightEngineObjectEnum.InsightEngine)->search_utils.SearchResult:
        try:
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["response_type","search_field", "search_value", "page_size", "page_number"])
            if search_value and search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            if search_value and not search_field in search_dictionary:
                search_dictionary[search_field]=[search_value]
            response_type = getattr(sys.modules["project_shkedia_models.insights"], response_type.value)
            insights_list = self.db_service.select(InsightEngineOrm,response_type,**search_dictionary)
            if insights_list is None:
                raise HTTPException(status_code=404, detail="Engine was not found")
            if not type(insights_list) is list:
                insights_list=[insights_list]
            return search_utils.page_result_formater(results=insights_list, page_size=page_size,page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")


    def search_insight(self, request: Request, search_field: str = "name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0, response_type: InsightObjectEnum = InsightObjectEnum.InsightBasic) -> search_utils.SearchResult:
        try:
            #TODO: Think about a way to get only the owners information (Option1: Include owners_id in the sql table, Option2: Use join)
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["response_type","search_field", "search_value", "page_size", "page_number"])
            if search_value and search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            if search_value and not search_field in search_dictionary:
                search_dictionary[search_field]=[search_value]
            response_type = getattr(sys.modules["project_shkedia_models.insights"], response_type.value)
            insights_list = self.db_service.select(InsightOrm,response_type,**search_dictionary)
            if insights_list is None:
                raise HTTPException(status_code=404, detail="Insight was not found")
            if not type(insights_list) is list:
                insights_list=[insights_list]
            return search_utils.page_result_formater(results=insights_list, page_size=page_size,page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def update_insight_engine(self, new_insight_engine: InsightEngine) -> InsightEngineBasic:
        try:
            updated_object = self.db_service.update(new_insight_engine, object_to_update=InsightEngineOrm, select_by_field="id")
            return sql_model_to_pydantic_model(updated_object, InsightEngineBasic)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500, detail="Can't Update media")