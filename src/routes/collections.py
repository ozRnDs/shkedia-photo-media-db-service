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
from models.collection import CollectionBasic, CollectionMedia, CollectionObjectEnum
from db.service import DBService
from logics.collections import CollectionLogicService
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
                           )
        router.add_api_route(path="/all",
                             endpoint=self.get_collections_list,
                             methods=["get"],
                             response_model=List[CollectionBasic])
        router.add_api_route(path="/{collection_name}",
                             endpoint=self.get_collection,
                             methods=["get"],
                             response_model=Union[List[CollectionBasic],List[CollectionMedia]])
        router.add_api_route(path="/search",
                             endpoint=self.search_collection,
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

    def get_collection(self, collection_name: str = None) -> List[CollectionMedia]: #, response_type: CollectionObjectEnum = CollectionObjectEnum.CollectionBasic):
        try:
            #TODO: Connect to collection logics
            results_dict = self.collection_logics.get_collections_metadata_by_names([collection_name])
            results=(list)(results_dict.values())
            if len(results)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The collection was not found")
            return results
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def search_collection(self, request: Request, search_field: str = "name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0, response_type: CollectionObjectEnum = CollectionObjectEnum.CollectionBasic) -> search_utils.SearchResult:
        pass