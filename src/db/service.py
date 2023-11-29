import logging
logger = logging.getLogger(__name__)
import json
import psycopg
from abc import ABC
from typing import Type, TypeVar

from db.sql_from_model import get_table_name_from_object

class SqlModel(ABC):

    @staticmethod
    def __sql_create_table__():
        raise NotImplementedError()

    def __sql_insert__(self):
        raise NotImplementedError()
    
    @staticmethod
    def __sql_select_item__(field_name, field_value):
        raise NotImplementedError()

    def __sql_update_item__(self):
        raise NotImplementedError()

    def __sql_delete_item__(self):
        raise NotImplementedError()

    def __does_table_exists__(self):
        table_name = get_table_name_from_object(self)
        sql_template = ...
        return ...

TSqlModel = TypeVar("TSqlModel", bound=SqlModel)

class DBService:

    def __init__(self,
                 credential_file_location: str,
                 connection_timeout: int=10
                 ) -> None:
        self.credential_file_location = credential_file_location
        credential_object = self.__get_credentials_from_file__()
        try:
            self.db_connection_object = psycopg.connect(host=credential_object["host"],
                                                        port=credential_object["port"],
                                                        dbname=credential_object["db_name"],
                                                        user=credential_object["user"],
                                                        password=credential_object["password"],
                                                        connect_timeout=connection_timeout)
        except Exception as err:
            logger.error(err)
            raise ConnectionError("Couldn't connect to the server")
        if self.db_connection_object.closed:
            raise ConnectionError("Couldn't connect to the server")
        logger.info("Connected Successfully to the DB")
    
    def __get_credentials_from_file__(self):
        with open(self.credential_file_location, 'r') as file:
            credential_object = json.load(file)
        return credential_object
    
    def is_ready(self):
        if not self.db_connection_object.closed:
            return True
        return False

    def create_table(self, model_type: Type[TSqlModel]) -> None:
        sql_template = model_type.__sql_create_table__()
        self.__execute_sql__(sql_template=sql_template, values=None, commit=True)

    def insert(self, model_type: Type[TSqlModel], **kargs) -> TSqlModel:
        model_object = model_type(**kargs)
        sql_template, values = model_object.__sql_insert__()
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)
        return model_object

    def select(self, model_type: Type[TSqlModel], **kargs) -> TSqlModel:
        search_key = (list)(kargs.keys())[0]
        search_value = (list)(kargs.values())[0]
        sql_template, values = model_type.__sql_select_item__(search_key, search_value)
        curser = self.__execute_sql__(sql_template=sql_template, values=values, get_cursor=True)
        responses = curser.fetchall()
        curser.close()
        models_list=[]
        for response in responses:
            models_list.append(self.__parse_response_to_model__(model_type, response))
        if len(models_list) == 1:
            return models_list[0]
        if len(models_list) > 0:
            return models_list
        return None
    
    @staticmethod
    def __parse_response_to_model__(model_type: Type[TSqlModel], values_list: list):
        fields = model_type.model_fields
        kargs = {}
        for field_index, field_name in enumerate(fields):
            if values_list[field_index] is None:
                continue
            # kargs[field_name] = eval(values_list[field_index])
            kargs[field_name] = (fields[field_name].annotation)(values_list[field_index])
        return model_type(**kargs)


    def delete(self, model_object: TSqlModel):
        sql_template, values = model_object.__sql_delete_item__()
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    def update(self, model_object: TSqlModel):
        sql_template, values = model_object.__sql_update_item__()
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    def __execute_sql__(self, sql_template, values: tuple, get_cursor=False, commit=False):
        temp_curser = self.db_connection_object.cursor()
        try:
            temp_curser.execute(sql_template, values)
            if commit:
                self.db_connection_object.commit()
            if get_cursor:
                return temp_curser
        except Exception as err:
            logger.error(err)
        temp_curser.close()
        

    def __is_changing_query__(self, query):
        if "INSERT INTO" in query:
            return True
        if "UPDATE" in query:
            return True
        if "CREATE" in query:
            return True
        if "DROP" in query:
            return True

    def __del__(self):
        self.close()

    def close(self):
        if not self.db_connection_object:
            return
        if self.db_connection_object.closed:
            return
        self.db_connection_object.close()
        logger.info("Closed DB Connection")

        
