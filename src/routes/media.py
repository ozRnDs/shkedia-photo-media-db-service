import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException, Depends
from typing import Union, List

from models.user import UserDB, User
from models.device import Device
from models.media import Media, MediaRequest
from db.service import DBService
from authentication.service import AuthService

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
                             response_model=Media)
        router.add_api_route(path="/search", 
                             endpoint=self.search_media,
                             methods=["get"],
                             response_model=Union[Media,List[Media]])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.get_media,
                             methods=["get"],
                             response_model=Media)
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.delete_media,
                             methods=["delete"])
        router.add_api_route(path="/{media_id}", 
                             endpoint=self.update_media,
                             methods=["post"],
                             response_model=Media)
        return router

    def put_media(self, media: MediaRequest) -> Media:
        try:
            #TODO: Get device and user id from the token
            device = self.db_service.select(Device, device_id=media.device_id)
            # if user is None:
            #     raise HTTPException(status_code=404, detail="Can't find user")
            if not device:
                logger.error(f"Device '{media.device_id}' does not exists")
            new_media = self.db_service.insert(Media, 
                                        **media.model_dump(),
                                        owner_id=device.owner_id)
            return new_media
        except Exception as err:
            if type(err) == HTTPException:
                raise err
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't create media")

    def get_media(self, media_id: str = None)-> Media:
        return self.search_media(search_field="media_id", search_value=media_id)
    

    def search_media(self, search_field: str = "media_name", search_value: str = None) -> Media:
        try:
            search_dictionary = {search_field: search_value}
            get_media: Media = self.db_service.select(Media,**search_dictionary)
            if get_media is None:
                raise HTTPException(status_code=404, detail="media was not found")
            return get_media
        except Exception as err:
            if type(err)==HTTPException:
                raise err
            logger.error(str(err))
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

    def update_media(self, media_id: str) -> Media:
        try:
            self.db_service.update(Media, media_id=media_id)
        except Exception as err:
            logger.error(err)
            raise HTTPException(status_code=500, detail="Can't Update media")