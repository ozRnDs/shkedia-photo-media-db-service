from pydantic import BaseModel, Field
from typing import Union
from uuid import uuid4
from datetime import datetime

from db.service import SqlModel

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
    media_thumbnail: str
    media_type: str
    media_size_bytes: int
    created_on: str
    device_id: str
    device_media_uri: str  

class Media(BaseModel, SqlModel):
    media_id: str = Field(default_factory=lambda:str(uuid4()))
    media_name: str
    media_type: MediaType
    media_size_bytes: int
    media_thumbnail: str
    created_on: str    
    upload_status: MediaUploadStatus = MediaUploadStatus.PENDING
    device_id: str
    device_media_uri: str
    media_status_on_device: MediaDeviceStatus = MediaDeviceStatus.EXISTS
    owner_id: str # Extract from the device information
    storage_service_name: str | None = None
    storage_bucket_name: str | None = None
    storage_media_uri: str | None = None
    media_key: str | None = None

    @staticmethod
    def __sql_create_table__():
        sql_template = """CREATE TABLE IF NOT EXISTS medias (
            media_id VARCHAR ( 50 ) PRIMARY KEY,
            media_name VARCHAR ( 250 ) UNIQUE NOT NULL,
            media_type VARCHAR ( 50 ) NOT NULL,
            media_size_bytes INTEGER NOT NULL,
            media_thumbnail VARCHAR ( 50 ),
            created_on TIMESTAMP NOT NULL,
            upload_status VARCHAR ( 50 ) NOT NULL,
            device_id VARCHAR ( 50 ) NOT NULL REFERENCES devices(device_id),
            device_media_uri VARCHAR ( 250 ) NOT NULL,
            media_status_on_device VARCHAR ( 50 ) NOT NULL,
            owner_id VARCHAR ( 50 ) NOT NULL REFERENCES users(user_id),
            storage_service_name VARCHAR ( 50 ),
            storage_bucket_name VARCHAR ( 50 ),
            storage_media_uri VARCHAR ( 250 ),
            media_key VARCHAR ( 2048 )
        )"""
        return sql_template
    
    def __sql_insert__(self):
        sql_template = """INSERT INTO devices (
            device_id, device_name, owner_id, created_on, device_status
        ) VALUES (%s, %s, %s, %s, %s)"""
        values = (self.device_id, self.device_name, self.owner_id, self.created_on, self.status)
        return sql_template, values

    @staticmethod
    def __sql_select_item__(field_name, field_value):
        sql_template = f"SELECT * FROM devices WHERE {field_name}=%s"
        return sql_template, (field_value,)
