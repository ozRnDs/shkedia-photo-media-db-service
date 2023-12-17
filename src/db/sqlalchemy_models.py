from sqlalchemy import String, ForeignKey, Text, DateTime, Enum, Integer, SmallInteger, PickleType
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List
from uuid import uuid4

from datetime import datetime

ENVIRONMENT = "dev0"

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users_"+ENVIRONMENT

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid4()))
    user_name: Mapped[str] = mapped_column(String(50), unique=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    password: Mapped[str] = mapped_column(String(250))
    devices: Mapped[List["Device"]] = relationship(back_populates="owner")
    media: Mapped[List["Media"]] = relationship(back_populates="owner")

class Device(Base):
    __tablename__ = "devices_"+ENVIRONMENT

    device_id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid4()))
    device_name: Mapped[str] = mapped_column(String(50), unique=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    device_status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # ENUM: ACTIVE, DEACTIVATED
    owner_id: Mapped[str] = mapped_column(ForeignKey("users_"+ENVIRONMENT+".user_id"))
    owner: Mapped["User"] = relationship(back_populates="devices")
    media: Mapped[List["Media"]] = relationship(back_populates="device")

class Media(Base):
    __tablename__ = "media_"+ENVIRONMENT

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid4()))
    media_name: Mapped[str] = mapped_column(String(250))
    media_type: Mapped[str] = mapped_column(String(50))
    media_size_bytes: Mapped[int] = mapped_column(Integer)
    media_description: Mapped[Optional[str]] = mapped_column(Text)
    media_width: Mapped[Optional[int]] = mapped_column(SmallInteger)
    media_height: Mapped[Optional[int]] = mapped_column(SmallInteger)
    media_thumbnail: Mapped[Optional[str]] = mapped_column(Text)
    media_thumbnail_width: Mapped[Optional[int]] = mapped_column(SmallInteger)
    media_thumbnail_height: Mapped[Optional[int]] = mapped_column(SmallInteger)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    device_id: Mapped[str] = mapped_column(ForeignKey("devices_"+ENVIRONMENT+".device_id"))
    device_media_uri: Mapped[str] = mapped_column(String(250))
    upload_status: Mapped[str] = mapped_column(String(50), default="PENDING") # ENUM: PENDING, UPLOADED
    media_status_on_device: Mapped[str] = mapped_column(String(50), default="EXISTS") # ENUM: EXISTS, DELETED
    owner_id: Mapped[str] = mapped_column(ForeignKey("users_"+ENVIRONMENT+".user_id"))
    storage_service_name: Mapped[Optional[str]] = mapped_column(String(50))
    storage_bucket_name: Mapped[Optional[str]] = mapped_column(String(50))
    storage_media_uri: Mapped[Optional[str]] = mapped_column(String(50))
    media_key: Mapped[Optional[str]] = mapped_column(String(2048))

    device: Mapped["Device"] = relationship(back_populates="media")
    owner: Mapped["User"] = relationship(back_populates="media")
    insights: Mapped[List["Insight"]] = relationship(back_populates="media")
    insight_jobs: Mapped[List["InsightJob"]] = relationship(back_populates="media")


class InsightEngine(Base):
    __tablename__ =  "insight_engine_"+ENVIRONMENT

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250))
    description: Mapped[Optional[str]] = mapped_column(Text())
    input_source: Mapped[str] = mapped_column(String(250))
    input_queue_name: Mapped[str] = mapped_column(String(250))
    output_exchange_name: Mapped[str] = mapped_column(String(250))
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") #ENUM: ACTIVE, DEACTIVATED

    jobs: Mapped[List["InsightJob"]] = relationship(back_populates="insight_engine")
    insights: Mapped[List["Insight"]] = relationship(back_populates="insight_engine")

class Insight(Base):
    __tablename__ = "insights_"+ENVIRONMENT

    id: Mapped[int] = mapped_column(primary_key=True)
    insight_engine_id: Mapped[int] = mapped_column(ForeignKey("insight_engine_"+ENVIRONMENT+".id"))
    media_id: Mapped[str] = mapped_column(ForeignKey("media_"+ENVIRONMENT+".id"))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    bounding_box: Mapped[Optional[List[int]]] = mapped_column(PickleType())
    status: Mapped[str] = mapped_column(String(50), default="COMPUTED") # ENUM: COMPUTED, APPROVED, REJECTED

    media: Mapped["Media"] = relationship(back_populates="insights")
    insight_engine: Mapped["InsightEngine"] = relationship(back_populates="insights")

class InsightJob(Base):
    __tablename__ = "insight_jobs_"+ENVIRONMENT

    id: Mapped[int] = mapped_column(primary_key=True)
    insight_engine_id: Mapped[int] = mapped_column(ForeignKey("insight_engine_"+ENVIRONMENT+".id"))
    media_id: Mapped[str] = mapped_column(ForeignKey("media_"+ENVIRONMENT+".id"))
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # ENUM: PENDING, FAILED, DONE, CANCELED
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    net_time_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    media: Mapped["Media"] = relationship(back_populates="insight_jobs")
    insight_engine: Mapped["InsightEngine"] = relationship(back_populates="jobs")