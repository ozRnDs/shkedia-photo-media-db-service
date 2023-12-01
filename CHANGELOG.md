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
