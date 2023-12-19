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


from db.sql_models import Device, Media
from models.media import MediaDB, MediaRequest, MediaObjectEnum, MediaIDs, MediaDevice, MediaMetadata, MediaStorage, MediaThumbnail
from db.service import DBService
from authentication.service import AuthService
from models.parser import sql_model_to_pydantic_model
from . import search_utils

class MediaServiceHandler:
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
        router = APIRouter(tags=["Medias"],
                        #    dependencies=[Depends(self.auth_service.__get_user_from_token__)],
                           )
        router.add_api_route(path="", 
                             endpoint=self.put_media,
                             methods=["put"],
                             response_model=MediaDB)
        router.add_api_route(path="/search", 
                             endpoint=self.search_media,
                             methods=["get"],
                             response_model=search_utils.SearchResult)
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.get_media,
                             methods=["get"],
                             response_model=Union[MediaIDs, MediaDevice, MediaMetadata, MediaThumbnail, MediaStorage])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.delete_media,
                             methods=["delete"])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.update_media,
                             methods=["post"],
                             response_model=MediaDB)
        return router

    def __get_device_from_sql__(self, device_id) -> Device:
        device = None
        find_device = sqlalchemy.select(Device).where(Device.device_id==device_id)
        with Session(self.db_service.db_sql_engine) as session:
            device = session.execute(find_device).first()
        return device

    def put_media(self, media: MediaRequest) -> MediaDB:
        try:
            device = self.__get_device_from_sql__(self, media.device_id)
            if not device:
                err_detail = f"Device '{media.device_id}' does not exists"
                logger.error(err_detail)
                raise HTTPException(status_code=400, detail=err_detail)
            raise NotImplementedError("Need to create the SQL Model here")
            new_media = self.db_service.insert(MediaDB, 
                                        **media.model_dump(),
                                        owner_id=device.owner_id)
            return new_media
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create media")

    def get_media(self, media_id: str = None, response_type: MediaObjectEnum = MediaObjectEnum.MediaIDs):
        #TODO: Rewrite using the search_media new helpers, consider adding the response_type option
        media = None
        find_media = sqlalchemy.select(Media).where(Media.media_id==media_id)
        with Session(self.db_service.db_sql_engine) as session:
            media = session.execute(find_media).first()
        return media
    

    def search_media(self, request: Request, search_field: str = "media_name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0, response_type: MediaObjectEnum = MediaObjectEnum.MediaIDs) -> search_utils.SearchResult:
        #TODO: Add all the Media Models to the fastapi models list.
        try:
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["response_type","search_field", "search_value", "page_size", "page_number"])
            if search_value and search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            if search_value and not search_field in search_dictionary:
                search_dictionary[search_field]=[search_value]
            response_type = getattr(sys.modules["models.media"], response_type.value)
            get_media = self.db_service.select(Media,response_type,**search_dictionary)
            if get_media is None:
                raise HTTPException(status_code=404, detail="media was not found")
            if not type(get_media) is list:
                get_media=[get_media]
            return search_utils.page_result_formater(results=get_media, page_size=page_size,page_number=page_number)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def delete_media(self, media_id: str):
        # TODO: Refactor and adjust to sqlalchemy
        try:
            media = self.db_service.select(media, media_id=media_id)
            if media is None:
                raise HTTPException(status_code=404, detail="Can't delete media")
            self.db_service.delete(media)
            return True
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't delete media")

    def update_media(self, new_media: MediaDB) -> MediaDB:
        # TODO: Refactor and adjust to sqlalchemy
        try:
            current_media = self.get_media(media_id=new_media.media_id)
            self.db_service.update(current_media,new_media)
            return new_media
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500, detail="Can't Update media")