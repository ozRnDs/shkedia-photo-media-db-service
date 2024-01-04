import logging
logger = logging.getLogger(__name__)
import json
import sqlalchemy
from typing import List, Any
from sqlalchemy.orm import Session, attributes
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
                session.expire_on_commit=False
                session.add_all(items)
                session.commit()
                return True
            except Exception as err:
                session.rollback()
                logger.error(err)
                return False

    def select_all(self, model_type: Base, output_model: BaseModel=None):
        select_list = [model_type]
        if not output_model is None:
            select_dict = {field:model_type.__dict__[field] for field in output_model.model_fields if field in model_type.__dict__}
            select_list = (list)(select_dict.values())
            keys_list = (list)(select_dict.keys())
        
        sql_query = sqlalchemy.select(*select_list)

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

    def get_columns_from_models(self,model_type: Base, output_model:BaseModel=None):
        select_list = [model_type]
        if not output_model is None:   
            select_dict = {field:model_type.__dict__[field] for field in output_model.model_fields if field in model_type.__dict__}
            select_list = (list)(select_dict.values())
            keys_list = (list)(select_dict.keys())
        return keys_list,select_list

    def convert_results_to_orm(self, results, keys_list, output_model:BaseModel):
        results_orm = []
        for result in results:
            result_dict = {keys_list[index]:value for index,value in enumerate(result) if not value is None}
            results_orm.append(output_model(**result_dict))
        return results_orm

    def select(self, model_type: Base,output_model:BaseModel=None,distinct: bool = False,order_by: attributes.InstrumentedAttribute | None = None, **kargs):
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
        if distinct:
            sql_query=sql_query.distinct()
        if order_by:
            sql_query=sql_query.order_by(order_by)
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

    
    # def delete(self, items: List[Base]):
    #     sql_template, values = model_object.__sql_delete_item__(self.environment)
    #     self.__execute_sql__(sql_template=sql_template, values=values, commit=True)

    def update(self, new_model_object: BaseModel, object_to_update, select_by_field: str, user_id: str=None):
        """Updates single pydantic object in the sql model based on the ORM model and search field.

        Args:
            new_model_object (BaseModel): Pydantic model with the updated data
            object_to_update (Base): The ORM model class based on sqlalchemy
            select_by_field (str): The name of the field to set the update from

        Raises:
            FileNotFoundError: If could not find any object to update

        Returns:
            _type_: The result object after it was updated
        """        
        search_in_field = object_to_update.__dict__[select_by_field]
        value_of_field = new_model_object.model_dump()[select_by_field]
        update_query = sqlalchemy.select(object_to_update).where(search_in_field==value_of_field)
        if "owner_id" in object_to_update.__dict__:
            owner_column = object_to_update.__dict__["owner_id"]
            update_query = update_query.where(owner_column==user_id)
        with Session(self.db_sql_engine) as session:
            session.expire_on_commit = False
            result = session.scalars(update_query).first()
            if not result:
                raise FileNotFoundError(f"Could not find an object to update. {search_in_field}=={value_of_field}")
            for field in new_model_object.model_dump().keys():
                value = getattr(new_model_object,field)
                if value != getattr(result,field):
                    setattr(result,field,value)
            # session.flush()
            session.commit()
        return result              


    def select_anti_join(self, model_type: Base, anti_join_statement, output_model: BaseModel=None, **kargs):
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

        anti_join_query = sqlalchemy.exists().where(anti_join_statement).where()
        sql_query = sqlalchemy.select(*select_list).filter(~anti_join_query).where(sqlalchemy.and_(*search_conditions))
    
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

    # def close(self):
    #     if not self.db_sql_engine:
    #         return
    #     if self.db_sql_engine.closed:
    #         return
    #     self.db_sql_engine.close()
    #     logger.info("Closed DB Connection") 
