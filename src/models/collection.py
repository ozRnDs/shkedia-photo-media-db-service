from pydantic import BaseModel, Field
from typing import Union, TypeVar, Type, List
from uuid import uuid4
from datetime import datetime

from enum import Enum

class CollectionObjectEnum(str, Enum):
    CollectionBasic="CollectionBasic"
    CollectionMedia="CollectionMedia"


class CollectionBasic(BaseModel):
    name: str
    engine_name: str

class CollectionMedia(CollectionBasic):
    media_list: List[str] = []
    thumbnail: str | None = None