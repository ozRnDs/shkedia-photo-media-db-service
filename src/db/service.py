import logging
logger = logging.getLogger(__name__)
import json
import psycopg
from psycopg.errors import OperationalError
from abc import ABC
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from db.sql_from_model import get_table_name_from_object

class SqlModel():

    @staticmethod
    def __sql_create_table__(environment: str):
        raise NotImplementedError()

    def __sql_insert__(self, environment: str):
        raise NotImplementedError()
    
    @staticmethod
    def __sql_select_item__(field_name, field_value, environment: str):
        raise NotImplementedError()

    def __sql_update_item__(self, environment: str):
        raise NotImplementedError()

    def __sql_delete_item__(self, environment: str):
        raise NotImplementedError()

    def __does_table_exists__(self):
        raise NotImplementedError("I still don't know that. In the near future")
        table_name = get_table_name_from_object(self)
        sql_template = ...
        return ...

    def __get_updated_values__(self: BaseModel, updated_model: BaseModel):
        current_dictionary = self.model_dump()
        new_dictionary = updated_model.model_dump()
        # Make sure the item's id can't change - extract it from update_model
        id_field_name = type(self).__name__.lower().replace("db","") + "_id"
        new_dictionary.pop(id_field_name)
        current_dictionary.pop(id_field_name)

        update_dictionary = {}
        for field_name, field_value in current_dictionary.items():
            if not field_name in new_dictionary:
                update_dictionary[field_name]=new_dictionary[field_name]
                continue
            if field_value != new_dictionary[field_name]:
                update_dictionary[field_name]=new_dictionary[field_name]
        return update_dictionary

TSqlModel = TypeVar("TSqlModel", bound=SqlModel)

class DBService:

    def __init__(self,
                 credential_file_location: str,
                 connection_timeout: int=10,
                 environment: str = "dev"
                 ) -> None:
        self.credential_file_location = credential_file_location
        self.connection_timeout = connection_timeout
        self.environment = environment.lower()
        try:
            self.db_connection_object: psycopg.Connection = None
            self.__connect__()
        except Exception as err:
            logger.error(err)
            raise ConnectionError("Couldn't connect to the server")
        if self.db_connection_object.closed:
            raise ConnectionError("Couldn't connect to the server")
        logger.info("Connected Successfully to the DB")
    
    def __connect__(self):
        credential_object = self.__get_credentials_from_file__()
        self.db_connection_object = psycopg.connect(host=credential_object["host"],
                        port=credential_object["port"],
                        dbname=credential_object["db_name"],
                        user=credential_object["user"],
                        password=credential_object["password"],
                        connect_timeout=self.connection_timeout,
                        autocommit=True)

    def __get_credentials_from_file__(self):
        with open(self.credential_file_location, 'r') as file:
            credential_object = json.load(file)
        return credential_object
    
    def is_ready(self):
        if not self.db_connection_object.closed:
            return True
        return False

    def create_table(self, model_type: Type[TSqlModel]) -> None:
        sql_template = model_type.__sql_create_table__(self.environment)
        self.__execute_sql__(sql_template=sql_template, values=None, commit=True)

    def insert(self, model_type: Type[TSqlModel], **kargs) -> TSqlModel:
        model_object = model_type(**kargs)
        sql_template, values = model_object.__sql_insert__(self.environment)
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)
        return model_object

    def select(self, model_type: Type[TSqlModel], **kargs) -> TSqlModel:
        search_keys = (list)(kargs.keys())
        search_values = (list)(kargs.values())
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
    
    def delete(self, model_object: TSqlModel):
        sql_template, values = model_object.__sql_delete_item__(self.environment)
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    def update(self, current_model_object: TSqlModel, new_model_object: TSqlModel):
        sql_template, values = current_model_object.__sql_update_item__(new_model_object, self.environment)
        self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    def close(self):
        if not self.db_connection_object:
            return
        if self.db_connection_object.closed:
            return
        self.db_connection_object.close()
        logger.info("Closed DB Connection")

    def __execute_sql__(self, sql_template, values: tuple, get_cursor=False, commit=False, retry=0):
        if self.db_connection_object.closed:
            logger.info("Reconnect to DB Service")
            self.__connect__()
        temp_curser = self.db_connection_object.cursor()
        try:
            temp_curser.execute(sql_template, values)
            # if commit:
            #     self.db_connection_object.commit()
            if get_cursor:
                return temp_curser
            temp_curser.close()
            return
        except OperationalError as err:
            if "EOF detected" in str(err):
                if not temp_curser.closed:
                    temp_curser.close()
                if retry>10:
                    raise err
                return self.__execute_sql__(sql_template=sql_template,
                                            values=values,
                                            get_cursor=get_cursor,
                                            commit=commit,
                                            retry=retry+1)
        except Exception as err:
            if not temp_curser.closed:
                temp_curser.close()
            logger.error(err)
            raise err
 
    @staticmethod
    def __parse_response_to_model__(model_type: Type[TSqlModel], values_list: list, columns: list):
        kargs = {}
        for field_index, field_name in enumerate(columns):
            if values_list[field_index] is None:
                continue
            # kargs[field_name] = eval(values_list[field_index])
            kargs[field_name] = values_list[field_index]
        return model_type(**kargs)        

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



        
