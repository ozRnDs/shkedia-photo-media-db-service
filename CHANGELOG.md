## 0.8.1 (2024-01-07)

### Fix

- **routes/media**: Fix the order in the request of update_media, to try the child object first

## 0.8.0 (2024-01-06)

### Feat

- **routes/insights_v3**: Return distinct values to the route that returns all the engines
- **InsightOrm**: Add prob field. Create migration for dev0

### Fix

- **login/collection**: Add distinct filter to get_media_by_collection, get_collections_metadata

## 0.7.0 (2024-01-05)

### Feat

- **routes/collections**: Add route to get media for collection. Improve collections routes endpoints naming
- **db/user_service**: Get current user details from auth micro-service
- **authentication/service**: Support auth_service token received from client. Get user data using that token
- **routes/media,routes/insights_v3,db/service**: Add authentication and authorizations to selected routes
- **collections**: Add auth to selected routes and get only logged-in user's information
- **authentication**: Implement the authentication service. It uses the project authentication micro-service
- **routes/insights_v3**: Add response with engine distict values. Improve api end-point naming
- **logics/collections,routes/collections**: Add logics to get medias to preview collection. Fix get collection by engine
- **routes/insights**: Add engine/search route
- **routes/jobs**: Add post /job to update jobs

### Fix

- **CollectionLogicService**: Get collections metadata by collection and engine name
- **authentication/service**: Catch errors in auth_request and raise HTTPException
- **logics/collection**: Add media_key to the CollectionPreview
- **db/sql_models**: Add unique constrain to all ids
- **logics/collections**: Repair the thumbnail return structure
- **routes/jobs**: Position /jobs/search before /jobs/{engine_name}. Fix errors in get_list_of_jobs_for_engine. Prevent response for non existing engine in no_jobs route
- **sql_models**: Update the mapping between InsightJobOrm and InsightOrm
- **routes/job**: Add filter to no_job route based on the uploaded status

### Refactor

- **config,auth/service,db/sql_models,routes/collections,routes/media**: Style and pylint fixes
- **routes,logics,db**: Export models folder to project-shkedia-models library
- **main.py**: Disable table creation on application startup
- **db,models**: Add connection between job and insights created from that job

## 0.6.0 (2023-12-28)

### Feat

- **routes/jobs**: Added new routes for searching and creating jobs and medias without jobs

### Refactor

- **db/service**: Create helper functions that converts between the Pydantic to the sqlalchemy queries inputs and outputs
- **models/media**: Move the field upload_status from MediaDevice to MediaIDs

## 0.5.1 (2023-12-25)

### Fix

- **db/sql_models.py**: Pull the environment suffix for the tables from os.environ

## 0.5.0 (2023-12-25)

### Feat

- **logics/collections,routes/collections**: Add a collection routes for getting media per collection and engine
- **insights**: Add route to handle that basic CRUd actions of the insights objects
- **routes/media,models/media,db/sql_models,db/service**: Improve the search flexiblity. Can return from the sql only the information needed for the request

### Fix

- **routes/media/get_media**: Adjust the route to sqlalchemy and use multiple return types
- **main,authentication/service**: Change the sqlalchemy_models to sql_models

### Refactor

- **logic/collection,route/collection**: Fix and Refactor get_collection in the route/collection. Extract the logics to different service
- **routes/collections**: Extract thumbnail for all collections with one query
- **models/collection,-routes/collection**: Create the basics of the collections. Not connected to the main.py yet
- **routes/media,db/service**: Update the routes response_models, disable the delete route and update only changed columns
- **routes/media,db,tests/conftest,tests/test_media_route**: Refactor the put_media route to use sqlalchemy
- **routes/media,db/service**: Create sqlalchemy implementation to the update route for medias
- **models/parser**: Create general parser that converts any sql orm (Base) to any pydantic object (BaseModel)
- **main,config,models/media,routes/media**: Adjust to sqlalchemy. Not done with the models and routes
- **authentication/service**: Adjust to sqlalchemy
- **db**: Use sqlalchemy in the db instead of pure sql code

## 0.4.1 (2023-12-07)

### Fix

- **db/service**: Get columns names from sql and use it in __parse_response_to_model__. The fix decouples the columns order in the sql and in the python model

## 0.4.0 (2023-12-07)

### Feat

- **models/media**: Add exif record to media

## 0.3.1 (2023-12-01)

### Fix

- **models/media/sql_create_table**: Change media_thumbnail type to TEXT in the sql statement
- **routes/media/get_media**: Return single result from SearchResult

## 0.3.0 (2023-12-01)

### Feat

- **routes/media**: Change the return object of search_media to SearchResult

## 0.2.0 (2023-12-01)

### Feat

- **models**: Create tables to each environment. Base on ENVIRONMENT in the configuration

## 0.1.2 (2023-11-30)

### Fix

- **routes/media/search_media**: If search_value in query is None don't add the search_field to the search_dictionary

## 0.1.1 (2023-11-30)

### Fix

- **db/service**: __connect__ funcation was missing, copied from auth service

## 0.1.0 (2023-11-29)

### Feat

- **main,models/media,routes/media,routes/search_utils**: Add CRU(D) actions the MediaDB Object. Including complex search route and utils
- **db/service**: Add generic updated_value logics. Enable autocommit on the connection. Upgrade the select function to handle multiple search parameters. Add error handlers for connection time out (in __execute_sql__). Adjust __parse_response_to_model__ to support more types and values
- **src**: Copy the RestAPI template and create Media object and Route

### Fix

- **routes/media/put_media**: Return HTTPException if device was not found
- **models/device,routes/media**: Adjust the device select function to the new version (using IN sql statment). Update the put routes to call correctly to the function
- **main**: Fix missing / in route prefix

### Refactor

- **models/device**: Change the create_on from str to datetime (to better support parsing)
- **project**: Initialize the project version and ide settings
