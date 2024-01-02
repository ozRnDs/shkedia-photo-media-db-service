import logging
logger = logging.getLogger(__name__)
from typing import Union, List, Annotated, Dict
import sqlalchemy
from sqlalchemy.orm import Session
from enum import Enum

# from models.user import UserDB, User
# from models.device import Device


from db.sql_models import InsightEngineOrm, InsightOrm, MediaOrm
from models.collection import CollectionBasic, CollectionPreview, CollectionObjectEnum
from db.service import DBService
from authentication.service import AuthService
from enum import Enum
from models.media import MediaThumbnail

class CollectionSearchField(str, Enum):
    ENGINE_NAME="ENGINE_NAME"
    COLLECTION_NAME="COLLECTION_NAME"


class CollectionLogicService:
    def __init__(self, 
                 db_service: DBService,
                 app_logging_service,
                 auth_service: AuthService
                 ):
        self.db_service = db_service
        self.logging_service = app_logging_service
        if not self.db_service.is_ready():
            raise Exception("Can't initializes without db_service")
        
    def get_collections_metadata_by_names(self,collections_names: List[str],
                                          field_name: CollectionSearchField = CollectionSearchField.COLLECTION_NAME,
                                          ) -> Dict[str,CollectionPreview]:
        
        insight_table = sqlalchemy.alias(InsightOrm)
        engine_table = sqlalchemy.alias(InsightEngineOrm)
        media_table = sqlalchemy.alias(MediaOrm)
        
        match field_name:
            case CollectionSearchField.ENGINE_NAME:
                search_field = engine_table.c.name
            case CollectionSearchField.COLLECTION_NAME:
                search_field = insight_table.c.name
        
        sql_query = sqlalchemy.select(insight_table.c.name, 
                                        engine_table.c.name, 
                                        media_table.c.media_id)
        sql_query = sql_query.join(engine_table, insight_table.c.insight_engine_id == engine_table.c.id)
        sql_query=sql_query.join(media_table,media_table.c.media_id==insight_table.c.media_id)
        sql_query=sql_query.where(search_field.in_(collections_names)).order_by(insight_table.c.name)
        results_dict = {}
        with Session(self.db_service.db_sql_engine) as session:
            results = session.execute(sql_query).fetchall()
            for result in results:
                temp_collection_name = result[0]
                engine_name = result[1]
                media_id = result[2]
                key = f"{engine_name}_{temp_collection_name}"
                if not key in results_dict:
                    results_dict[key]=CollectionPreview(name=temp_collection_name, engine_name=engine_name)
                results_dict[key].media_list.append(media_id)
            media_ids = [result.media_list[0] for _,result in results_dict.items()]
            thumbnails = self.__get_thumbnails_for_medias__(media_ids=media_ids,session=session)
            for media_id, thumbnail in thumbnails.items():
                for _,result in results_dict.items():
                    if result.thumbnail is None and media_id in result.media_list:
                        result.thumbnail = thumbnail
            return results_dict
        
    def get_media_by_collection_name(self,collection_name: str,
                                     page_number: int = 0, page_size: int = 16
                                          ) -> Dict[str,CollectionPreview]:
        insight_table = sqlalchemy.alias(InsightOrm)
        # media_table = sqlalchemy.alias(MediaOrm)

        keys_list, select_list = self.db_service.get_columns_from_models(MediaOrm, MediaThumbnail)
        #TODO: Get media details for preview
        sql_query = sqlalchemy.select(*select_list)
        sql_query=sql_query.join(insight_table,MediaOrm.media_id==insight_table.c.media_id)
        sql_query=sql_query.where(insight_table.c.name==collection_name).order_by(MediaOrm.created_on).offset(page_number*page_size).limit(page_size)
        with Session(self.db_service.db_sql_engine) as session:
            results = session.execute(sql_query).fetchall()
            results = self.db_service.convert_results_to_orm(results,keys_list,MediaThumbnail)
        return results



    def __get_thumbnails_for_medias__(self,media_ids: List[str], session: Session = None) -> Dict[str,str]:
        session_existed = True if session else False
        if not session:
            session = Session(self.db_service.db_sql_engine)
        get_thumbnail_query = sqlalchemy.select(MediaOrm.media_id,MediaOrm.media_thumbnail).where(MediaOrm.media_id.in_(media_ids))
        thumbnails = session.execute(get_thumbnail_query).fetchall()
        response_dict = {}
        for item in thumbnails:
            media_id, thumbnail = item
            response_dict[media_id] = thumbnail
        if not session_existed:
            session.close()
        return response_dict
