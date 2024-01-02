import traceback
import sys
import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import Union, List, Annotated
import sqlalchemy
from sqlalchemy.orm import Session
from enum import Enum

# from models.user import UserDB, User
# from models.device import Device


from db.sql_models import InsightEngineOrm, InsightOrm, MediaOrm
from models.collection import CollectionBasic, CollectionPreview, CollectionObjectEnum
from db.service import DBService
from logics.collections import CollectionLogicService, CollectionSearchField
from authentication.service import AuthService
from models.parser import sql_model_to_pydantic_model
from . import search_utils

class CollectionServiceHandler:
    def __init__(self, 
                 db_service: DBService,
                 app_logging_service,
                 auth_service: AuthService,
                 collection_logics: CollectionLogicService
                 ):
        self.db_service = db_service
        self.logging_service = app_logging_service
        self.auth_service = auth_service
        self.collection_logics = collection_logics
        if not self.db_service.is_ready():
            raise Exception("Can't initializes without db_service")
        self.router = self.__initialize_routes__()


    def __initialize_routes__(self):
        router = APIRouter(tags=["collection"],
                        #    dependencies=[Depends(self.auth_service.__get_user_from_token__)],
                           prefix=""
                           )
        router.add_api_route(path="/all",
                             endpoint=self.get_collections_list,
                             methods=["get"],
                             response_model=List[CollectionBasic])
        router.add_api_route(path="/{collection_name}/{page_number}",
                             endpoint=self.get_collection_by_name,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="",
                             endpoint=self.get_collection_by_engine,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        return router
    
    def get_collections_list(self, response_type: CollectionObjectEnum = CollectionObjectEnum.CollectionBasic) -> List[CollectionBasic]:
        try:
            response_type = getattr(sys.modules["models.collection"], response_type.value)
            sql_query = sqlalchemy.select(InsightOrm.name,InsightEngineOrm.name).join(InsightEngineOrm.insights).distinct()
            with Session(self.db_service.db_sql_engine) as session:
                results = session.execute(sql_query).fetchall()
                results = [CollectionBasic(name=result[0], engine_name=result[1]) for result in results]
            return results
        except Exception as err:
            logger.error(str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sorry, Something is wrong. Try again later")

    def get_collection_by_engine(self, engine_name: str = None, page_number: int = 0, page_size: int=16) -> search_utils.SearchResult:
        try:
            results_dict = self.collection_logics.get_collections_metadata_by_names([engine_name], field_name=CollectionSearchField.ENGINE_NAME)
            results=(list)(results_dict.values())
            return search_utils.page_result_formater(results,page_size,page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            traceback.print_exc()
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")


    def get_collection_by_name(self, collection_name: str = None, page_number: int = None, page_size: int = 16) -> search_utils.SearchResult: #, response_type: CollectionObjectEnum = CollectionObjectEnum.CollectionBasic):
        #TODO: Change to result type to handle the medias paging
        try:
            results = self.collection_logics.get_media_by_collection_name(collection_name, page_number=page_number, page_size=page_size)
            if len(results)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The collection was not found")
            return search_utils.SearchResult(total_results_number=len(results), results=results, page_number=page_number, page_size=page_size)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            traceback.print_exc()
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

