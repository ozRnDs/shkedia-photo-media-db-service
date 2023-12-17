from pydantic import BaseModel, Field
from typing import Union, TypeVar, Type
from uuid import uuid4
from datetime import datetime

# from db.service import SqlModel

from enum import Enum

class MediaUploadStatus(str, Enum):
    PENDING="PENDING"
    UPLOADED="UPLOADED"
    DELETED="DELETED"

class MediaDeviceStatus(str, Enum):
    EXISTS="EXISTS"
    DELETED="DELETED"

class MediaType(str, Enum):
    IMAGE="IMAGE"
    VIDEO="VIDEO"

class MediaRequest(BaseModel):
    media_name: str
    media_type: str
    media_size_bytes: int
    media_description: str = "-"
    media_width: int | None = None
    media_height: int | None = None
    media_thumbnail: str | None = None
    media_thumbnail_width: int | None = None
    media_thumbnail_height: int | None = None
    created_on: datetime
    device_id: str
    device_media_uri: str
    exif: str | None = None

class MediaResponse(MediaRequest):
    media_id: str = Field(default_factory=lambda:str(uuid4()))
    upload_status: MediaUploadStatus = MediaUploadStatus.PENDING
    media_status_on_device: MediaDeviceStatus = MediaDeviceStatus.EXISTS
    owner_id: str

# TMediaModel = TypeVar("TMediaModel", bound=MediaRequest)

class MediaDB(MediaResponse):
    storage_service_name: str | None = None
    storage_bucket_name: str | None = None
    storage_media_uri: str | None = None
    media_key: str | None = None

    # def convert_type(self, target_model: Type[TMediaModel]) -> TMediaModel:
    #     input_dict = {}
    #     source_dict = self.model_dump()
    #     for field_name in target_model.model_fields:
    #         if field_name in source_dict and source_dict[field_name]:
    #             input_dict[field_name]=source_dict[field_name]
    #     return target_model(**input_dict)