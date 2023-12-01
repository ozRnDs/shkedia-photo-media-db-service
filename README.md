# shkedia-photo-media-db-service
# Overview
The media DB service for the ShkediPhoto Private Cloud System
It will handle the communication between the entire system and the database that will handle the crypted media's metadata db.
This will be CRUD RESTful API based on FastAPI.

## The service actions - v1
### Handle media
| Method | Route | Description | Input | Output | Notes |
| -- | -- | -- | -- | -- | -- |
| PUT | /v1/media | Upload new media information | MediaRequest Model | MediaDB Object | The device_id is the most important owner. In the future should be retreived by the token |
| GET | /v1/media/search?page_size=&page_number=&<search_field> | Get a media or list of medias according to the search parameters. The search parameters are fields in the MediDB Object | *page_size* - number of results if single http request<br>*page_number* - The specific "result page" that was retreived<br> *<search_field>* - Property to search by. **Example:** media_name=Test_Media&media_name=Test_Media2 -> will get all the medias with either names  | MediaDB or SearchResult objects | - |
| GET | /v1/media/{media_id} | Equals to path *v1/media/search?media_id= | media_id | MediaDB Object | - |
| DELETE | /v1/media/{media_id} | Deletes media from the db | media_id | MediaDB Object | NOT IMPLEMENTED |
| POST | /v1/media | Updates the media sent in the body | MediaDB object | MediaDB Object |

### Handle media's insights - Not Implemented
GET /v1/media/{media_id}/insights  
GET /v1/media/{media_id}/insight/{insight_type}  
POST /v1/media/{media_id}/insight  
UPDATE /v1/media/{media_id}/insights  
UPDATE /v1/media/{media_id}/insight/{insight_type}  
DELETE /v1/media/{media_id}/insights  
DELETE /v1/media/{media_id}/insight/{insight_type}  

### Advanced Search capabilities - Not Implemented
GET /v1/search/metadata?media_id=X&user_id=X&start_date=X&end_date=  
GET /v1/search/insights?object=X&person=  

### Security
UPDATE /v1/rotate_key

# Deploy
## Local Deployment
1. Set the location of the credentials files on the host:
    ```bash
    export MEDIA_DB_SERVICE_VERSION=$(cz version -p)
    ```
1. Create credentials token files as follows:
    ```bash
    # Create the folder to be mounted to the container
    if [ ! -d $HOST_MOUNT ]; then
        sudo mkdir $HOST_MOUNT
        sudo chown $USER $HOST_MOUNT
    fi
    # Create the postgres credentials file:
    export SQL_HOST=<write your sql host>
    export SQL_PORT=<write your sql port>
    export DB_NAME=<write your db name>
    export SQL_USER=<write your sql username>
    export SQL_PASSWORD=<write your SQL_PASSWORD>

    cat << EOT > $HOST_MOUNT/postgres_credentials.json
    '{"host": '${SQL_HOST}', "port": '${SQL_PORT}', "db_name": '${DB_NAME}', "user": '${SQL_USER}', "password": '${SQL_PASSWORD}'}'
    EOT
    ```
1. Create *media_db_env.env* file in .local folder with the service variables:
    ```bash
    export CREDENTIALS_FOLDER_NAME=/temp
    export AUTH_DB_CREDENTIALS_LOCATION=$CREDENTIALS_FOLDER_NAME/postgres_credentials.json
    export JWT_KEY_LOCATION=$CREDENTIALS_FOLDER_NAME/jwt_token
    export ENV=dev

    if [ ! -d .local ]; then
        sudo mkdir .local
    fi
    cat << EOT > .local/media_db_service_$ENV.env
    CREDENTIALS_FOLDER_NAME=$CREDENTIALS_FOLDER_NAME
    AUTH_DB_CREDENTIALS_LOCATION=$AUTH_DB_CREDENTIALS_LOCATION
    JWT_KEY_LOCATION=$JWT_KEY_LOCATION
    TOKEN_TIME_PERIOD=15
    ENVIRONMENT=$ENV
    EOT
    ```
1. Run the service using compose command:
    ```bash
    docker compose up -d
    ```
1. The env can be override by the following command:
    ```bash
    export MEDIA_DB_ENV=.local/media_db_service_${ENV}.env
    docker compose --env-file ${MEDIA_DB_ENV} up -d
    ```

# Development
## Environment

## Build
1. Set the parameters for the build
    ```bash
    export MEDIA_DB_SERVICE_VERSION=$(cz version -p)
    export IMAGE_NAME=shkedia-photo-media-db-service:${MEDIA_DB_SERVICE_VERSION}
    export IMAGE_FULL_NAME=public.ecr.aws/q2n5r5e8/ozrnds/${IMAGE_NAME}
    ```
2. Build the image
    ```bash
    docker build . -t ${IMAGE_FULL_NAME}
    ```
3. Push the image
    ```bash
    docker push ${IMAGE_FULL_NAME}
    ```
    Before pushing the image, make sure you are logged in

## Test
### Running Tests
1. Make sure you have all the requirements_dev.txt installed. It is essential for the tests
    ```bash
    pip install -r requirements_dev.txt
    ```
1. Run the tests using CLI
    ```bash
    pytest -s tests
    ```
    **IMPORTANT**: Many of the tests need a connection to the sql server as they are integration tests.
**NOTE**: It is possible and easy to run the tests using VScode. Just press the "play" arrow. All the configuration for it are in the .vscode folder. Just make sure to install the Python Extension