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

class MediaTypeEnum(str, Enum):
    IMAGE="IMAGE"
    VIDEO="VIDEO"

class MediaObjectEnum(str,Enum):
    MediaIDs = "MediaIDs"
    MediaThumbnail = "MediaThumbnail"
    MediaStorage = "MediaStorage"
    MediaMetadata = "MediaMetadata"
    MediaDevice = "MediaDevice"

class MediaIDs(BaseModel):
    media_id: str = Field(default_factory=lambda:str(uuid4()))
    device_id: str
    owner_id: str
    created_on: datetime
    media_name: str
    media_type: MediaTypeEnum
    upload_status: MediaUploadStatus = MediaUploadStatus.PENDING

class MediaMetadata(MediaIDs):
    media_size_bytes: int
    media_description: str = "-"
    media_width: int | None = None
    media_height: int | None = None
    exif: str | None = None

class MediaDevice(MediaIDs):
    device_media_uri: str
    media_status_on_device: MediaDeviceStatus = MediaDeviceStatus.EXISTS

class MediaThumbnail(MediaIDs):
    media_thumbnail: str | None = None
    media_thumbnail_width: int | None = None
    media_thumbnail_height: int | None = None
    media_key: str | None = None

class MediaStorage(MediaIDs):
    storage_service_name: str | None = None
    storage_bucket_name: str | None = None
    storage_media_uri: str | None = None
    media_key: str | None = None

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

class MediaDB(MediaResponse):
    storage_service_name: str | None = None
    storage_bucket_name: str | None = None
    storage_media_uri: str | None = None
    media_key: str | None = None