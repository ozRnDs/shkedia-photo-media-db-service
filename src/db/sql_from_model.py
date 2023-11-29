

def get_table_name_from_object(object_model):
    return object_model.__class__.__name__.lower()+"s"

def create_sql_insert_to_object(object_model):
    table_name = get_table_name_from_object(object_model=object_model)
    fields_name = []
    values_placeholders = []
    values = [table_name]
    for key in object_model.__annotations__:
        value = object_model.__getattribute__(key)
        if value:
            fields_name.append(key)
            values_placeholders.append("%s")
            values.append(value)
    field_names_str = ",".join(fields_name)
    values_placeholders = ",".join(values_placeholders)
    values_tuple = (tuple)(values)
    sql_template = f"INSERT INTO %s ({field_names_str}) VALUES ({values_placeholders})"
    return sql_template, values_tuple

def create_sql_table_for_object(object_model):
    table_name = get_table_name_from_object(object_model=object_model)


    sql_template = "CREATE TABLE %s ()"