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


from db.sql_models import DeviceOrm, MediaOrm
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

    def __get_device_from_sql__(self, device_id) -> DeviceOrm:
        device = None
        find_device = sqlalchemy.select(DeviceOrm).where(DeviceOrm.device_id==device_id)
        with Session(self.db_service.db_sql_engine) as session:
            device = session.execute(find_device).first()
        return device

    def put_media(self, media_list: List[MediaRequest]) -> List[MediaIDs]:
        try:
            # device = self.__get_device_from_sql__(self, media.device_id)
            devices_ids = list(set([media.device_id for media in media_list]))
            devices = self.db_service.select(DeviceOrm,device_id=devices_ids)
            if len(devices)==0:
                err_detail = f"No device was found for the requested media"
                logger.error(err_detail)
                raise HTTPException(status_code=400, detail=err_detail)
            devices_dict = {device.device_id:device.owner_id for device in devices}
            media_list = [MediaOrm(owner_id=devices_dict[media.device_id], **media.model_dump()) for media in media_list]
            if self.db_service.insert(media_list):
                return [MediaIDs(**media.__dict__) for media in media_list]
            raise HTTPException(status_code=500, detail="Couldn't insert the media")
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create media")

    def get_media(self, media_id: str = None, response_type: MediaObjectEnum = MediaObjectEnum.MediaIDs):
        try:
            response_type = getattr(sys.modules["models.media"], response_type.value)
            find_media = self.db_service.select(MediaOrm, response_type, **{"media_id": [media_id]})
            if find_media is None or len(find_media)==0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="media was not found")
            return find_media[0]
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Server Internal Error")

    def search_media(self, request: Request, search_field: str = "media_name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0, response_type: MediaObjectEnum = MediaObjectEnum.MediaIDs) -> search_utils.SearchResult:
        try:
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["response_type","search_field", "search_value", "page_size", "page_number"])
            if search_value and search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            if search_value and not search_field in search_dictionary:
                search_dictionary[search_field]=[search_value]
            response_type = getattr(sys.modules["models.media"], response_type.value)
            get_media = self.db_service.select(MediaOrm,response_type,**search_dictionary)
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

    def update_media(self, new_media: MediaDB) -> MediaIDs:
        try:
            updated_object = self.db_service.update(new_media, object_to_update=MediaOrm, select_by_field="media_id")
            return sql_model_to_pydantic_model(updated_object, MediaIDs)
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500, detail="Can't Update media")