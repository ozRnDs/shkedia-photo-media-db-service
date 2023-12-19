from db.sql_models import Base
from pydantic import BaseModel

def sql_model_to_pydantic_model(sql_object:Base, pydantic_class: BaseModel):
    sql_dict = sql_object.__dict__
    pydantic_fields = pydantic_class.model_fields
    input_dict = {}
    for key,value in sql_dict.items():
        if value is None:
            continue
        if key in pydantic_fields:
            input_dict[key]=value
    return pydantic_class(**input_dict)