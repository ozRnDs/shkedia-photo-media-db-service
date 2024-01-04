import sys
import traceback
import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from typing import Union, List, Annotated
import sqlalchemy
from sqlalchemy.orm import Session
from enum import Enum

# from models.user import UserDB, User
# from models.device import Device


from db.sql_models import InsightEngineOrm, InsightOrm, MediaOrm, InsightJobOrm
from db.service import DBService
from logics.collections import CollectionLogicService, CollectionSearchField
from authentication.service import AuthService
from project_shkedia_models.jobs import InsightJob
from project_shkedia_models.insights import InsightEngineBasic
from project_shkedia_models.media import MediaStorage, MediaUploadStatus
from . import search_utils

class JobsServiceHandler:
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
        router = APIRouter(tags=["Jobs"],
                        #    dependencies=[Depends(self.auth_service.__get_user_from_token__)],
                           prefix=""
                           )
        router.add_api_route(path="/jobs/search",
                             endpoint=self.search_jobs,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="/jobs/{engine_name}",
                             endpoint=self.get_list_of_jobs_for_engine,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="/no-jobs/media/{engine_name}",
                             endpoint=self.get_list_of_media_with_no_jobs_for_engine,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="/job",
                             methods=["put"],
                             endpoint=self.put_list_of_jobs,
                             response_model=List[InsightJob])
        router.add_api_route(path="/job",
                             methods=["post"],
                             endpoint=self.update_list_of_jobs,
                             response_model=List[InsightJob])
        return router
    
    def get_list_of_jobs_for_engine(self, engine_name: str,
                                    page_size: int | None = None,
                                    page_number: int=0):
        try:
            engine_list: InsightEngineOrm = self.db_service.select(InsightEngineOrm,InsightEngineBasic, name=[engine_name])
            jobs_list = self.db_service.select(InsightJobOrm, InsightJob, insight_engine_id=[engine.id for engine in engine_list])
            if jobs_list is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jobs were not found")
            if not type(jobs_list) is list:
                jobs_list=[jobs_list]
            return search_utils.page_result_formater(results=jobs_list, page_size=page_size, page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def get_list_of_media_with_no_jobs_for_engine(self, engine_name: str,
                                    page_size: int | None = None,
                                    page_number: int=0,
                                    uploaded_status: list[MediaUploadStatus] = Query(default=[])):
        try:
            output_model = MediaStorage
            keys_list, select_list = self.db_service.get_columns_from_models(MediaOrm,output_model)
            get_engine_id_query = sqlalchemy.select(InsightEngineOrm.id).where(InsightEngineOrm.name==engine_name)
            medias_with_jobs_query = sqlalchemy.select(InsightJobOrm.media_id).join(InsightEngineOrm,InsightJobOrm.insight_engine_id==InsightEngineOrm.id).where(InsightEngineOrm.name==engine_name)
            medias_without_jobs_query = sqlalchemy.select(*select_list).where(~MediaOrm.media_id.in_(medias_with_jobs_query))
            if uploaded_status and len(uploaded_status)>0:
                uploaded_status = [item.value for item in uploaded_status]
                medias_without_jobs_query = medias_without_jobs_query.where(MediaOrm.upload_status.in_(uploaded_status))
            with Session(self.db_service.db_sql_engine) as session:
                engine_id = session.execute(get_engine_id_query).fetchall()
                if len(engine_id)==0:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engine was not found")
                media_list = session.execute(medias_without_jobs_query).fetchall()
                output_media_list = self.db_service.convert_results_to_orm(media_list,keys_list,output_model)
            if output_media_list is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media were not found")
            if not type(output_media_list) is list:
                output_media_list=[output_media_list]
            return search_utils.page_result_formater(results=output_media_list, page_size=page_size, page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            traceback.print_exc()
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")


    def search_jobs(self, request: Request, search_field: str = "id", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0) -> search_utils.SearchResult:
        try:
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["response_type","search_field", "search_value", "page_size", "page_number"])
            if search_value and search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            if search_value and not search_field in search_dictionary:
                search_dictionary[search_field]=[search_value]
            response_type = InsightJob
            insights_list = self.db_service.select(InsightJobOrm,response_type,**search_dictionary)
            if insights_list is None:
                raise HTTPException(status_code=404, detail="Jobs were not found")
            if not type(insights_list) is list:
                insights_list=[insights_list]
            return search_utils.page_result_formater(results=insights_list, page_size=page_size,page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            traceback.print_exc()
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def put_list_of_jobs(self, jobs_list: List[InsightJob]) -> List[InsightJob]:
        try:
            insights_orm_list = [InsightJobOrm(**job.model_dump()) for job in jobs_list]
            if self.db_service.insert(insights_orm_list):
                return [InsightJob(**job.__dict__) for job in insights_orm_list]
            raise HTTPException(status_code=500, detail="Couldn't insert job")
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create engines")
        
    def update_list_of_jobs(self, jobs_list: List[InsightJob]) -> List[InsightJob]:
        try:
            failed=[]
            success = []
            for job in jobs_list:
                try:
                    result = self.db_service.update(job, object_to_update=InsightJobOrm, select_by_field="id")
                    success.append(InsightJob(**result.__dict__))
                except Exception as err:
                    failed.append(job.id)
            if len(success)==len(jobs_list):
                return success
            logger.error(f"Failed to update jobs: {failed}")
            raise HTTPException(status_code=500, detail=f"Couldn't update {len(failed)} jobs")
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create engines")