import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException, status, Request
from typing import Union, List, Annotated

from models.user import UserDB, User
from models.device import Device
from models.media import MediaDB, MediaRequest, MediaResponse
from db.service import DBService
from authentication.service import AuthService

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
                             response_model=Union[MediaDB,search_utils.SearchResult])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.get_media,
                             methods=["get"],
                             response_model=MediaDB)
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.delete_media,
                             methods=["delete"])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.update_media,
                             methods=["post"],
                             response_model=MediaDB)
        return router

    def put_media(self, media: MediaRequest) -> MediaDB:
        try:
            device = self.db_service.select(Device, device_id=media.device_id)
            if not device:
                logger.error(f"Device '{media.device_id}' does not exists")
            new_media = self.db_service.insert(MediaDB, 
                                        **media.model_dump(),
                                        owner_id=device.owner_id)
            return new_media
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create media")

    def get_media(self, media_id: str = None)-> MediaDB:
        return self.search_media(request=None, search_field="media_id", search_value=media_id)
    

    def search_media(self, request: Request, search_field: str = "media_name", 
                     search_value: str = None,
                     page_size: int | None = None,
                     page_number: int=0) -> MediaDB:
        try:
            search_dictionary = {}
            if request:
                search_dictionary = search_utils.extract_search_params_from_request(request.query_params.multi_items(),black_list_values=["search_field", "search_value", "page_size", "page_number"])
            if search_field in search_dictionary:
                search_dictionary[search_field].append(search_value)
            else:
                search_dictionary[search_field]=[search_value]
            get_media: MediaDB = self.db_service.select(MediaDB,**search_dictionary)
            if get_media is None:
                raise HTTPException(status_code=404, detail="media was not found")
            if type(get_media) == list:
                return search_utils.page_result_formater(results=get_media, page_size=page_size,page_number=page_number)
            return get_media
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
            if type(err)==AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            raise HTTPException(status_code=500,detail="Server Internal Error")

    def delete_media(self, media_id: str):
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