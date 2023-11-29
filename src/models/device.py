from pydantic import BaseModel, Field
from typing import Union
from uuid import uuid4
from datetime import datetime

from db.service import SqlModel

class DeviceRequest(BaseModel):
    device_name: str
    owner_name: str

class Device(BaseModel, SqlModel):
    device_id: str = Field(default_factory=lambda:str(uuid4()))
    device_name: str
    owner_id: str
    created_on: str = Field(default_factory=lambda:datetime.now().isoformat())
    status: str = "ACTIVE"

    @staticmethod
    def __sql_create_table__():
        sql_template = """CREATE TABLE IF NOT EXISTS devices (
            device_id VARCHAR ( 50 ) PRIMARY KEY,
            device_name VARCHAR ( 50 ) UNIQUE NOT NULL,
            owner_id VARCHAR ( 50 ) NOT NULL REFERENCES users(user_id),
            created_on TIMESTAMP NOT NULL,
            device_status VARCHAR ( 50 )
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
