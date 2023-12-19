import logging
logger = logging.getLogger(__name__)
import json
import sqlalchemy
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.sql_models import Base, DeclarativeBase

class DBService:

    def __init__(self,
                 credential_file_location: str,
                 connection_timeout: int=10,
                 environment: str = "dev",
                 debug: bool = False
                 ) -> None:
        self.credential_file_location = credential_file_location
        self.connection_timeout = connection_timeout
        self.environment = environment.lower()
        self.debug = debug
        try:
            self.db_sql_engine: sqlalchemy.Engine = None
            self.__connect__()
        except Exception as err:
            logger.error(err)
            raise ConnectionError("Couldn't connect to the server")
        logger.info("Connected Successfully to the DB")
    
    def __connect__(self):
        credential_object = self.__get_credentials_from_file__()
        url = sqlalchemy.URL.create("postgresql+psycopg", username=credential_object["user"],
                             password=credential_object["password"],
                             host=credential_object["host"],
                             port=credential_object["port"],
                             database=credential_object["db_name"])
        self.db_sql_engine = sqlalchemy.create_engine(url, echo=self.debug)

    def __get_credentials_from_file__(self):
        with open(self.credential_file_location, 'r') as file:
            credential_object = json.load(file)
        return credential_object
    
    def is_ready(self):
        if self.db_sql_engine:
            return True
        return False

    def create_tables(self, table_decleration: DeclarativeBase) -> None:
        table_decleration.metadata.create_all(self.db_sql_engine)

    def insert(self, items: List[Base]) -> bool:
        with Session(self.db_sql_engine) as session:
            try:
                session.add_all(items)
                session.commit()
                return True
            except Exception as err:
                session.rollback()
                logger.error(err)
                return False

    def select(self, model_type: Base,output_model:BaseModel =None, **kargs):
        select_list = [model_type]
        if not output_model is None:   
            select_dict = {field:model_type.__dict__[field] for field in output_model.model_fields if field in model_type.__dict__}
            select_list = (list)(select_dict.values())
            keys_list = (list)(select_dict.keys())

        search_keys = (list)(kargs.keys())
        search_values = (list)(kargs.values())

        search_conditions=[]
        for index, key in enumerate(search_keys):
            search_column = model_type.__dict__[key]
            search_value = (list)(search_values[index])
            search_conditions.append(search_column.in_(search_value))

        sql_query = sqlalchemy.select(*select_list).where(sqlalchemy.and_(*search_conditions))
    
        with Session(self.db_sql_engine) as session:
            results = session.execute(sql_query).fetchall()
            if output_model is None:
                results_orm = [item[0] for item in results]
                return results_orm
            
            results_orm = []
            for result in results:
                result_dict = {keys_list[index]:value for index,value in enumerate(result) if not value is None}
                results_orm.append(output_model(**result_dict))
        
        return results_orm
        for search_key in search_keys:
            if not search_key in model_type.model_fields:
                raise AttributeError(f"Invalid Search Key: {search_key}")
        sql_template, values = model_type.__sql_select_item__(search_keys, search_values, self.environment)
        curser = self.__execute_sql__(sql_template=sql_template, values=values, get_cursor=True)
        columns = [desc[0] for desc in curser.description]
        responses = curser.fetchall()
        curser.close()
        models_list=[]
        for response in responses:
            models_list.append(self.__parse_response_to_model__(model_type, response, columns))
        if len(models_list) == 1:
            return models_list[0]
        if len(models_list) > 0:
            return models_list
        return None
    
    # def delete(self, items: List[Base]):
    #     sql_template, values = model_object.__sql_delete_item__(self.environment)
    #     self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    # def update(self, current_model_object: TSqlModel, new_model_object: TSqlModel):
    #     sql_template, values = current_model_object.__sql_update_item__(new_model_object, self.environment)
    #     self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    # def close(self):
    #     if not self.db_sql_engine:
    #         return
    #     if self.db_sql_engine.closed:
    #         return
    #     self.db_sql_engine.close()
    #     logger.info("Closed DB Connection") 
