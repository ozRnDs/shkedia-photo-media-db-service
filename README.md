# shkedia-photo-media-db-service
# Overview
The media DB service for the ShkediPhoto Private Cloud System
It will handle the communication between the entire system and the database that will handle the crypted media's metadata db.
This will be CRUD RESTful API based on FastAPI.

## The service actions
### Handle media
GET /v1/medias  
GET /v1/media/{media_id}  
POST /v1/media  
UPDATE /v1/media/{media_id}  
DELETE /v1/media/{media_id}  

### Handle media's insights
GET /v1/media/{media_id}/insights  
GET /v1/media/{media_id}/insight/{insight_type}  
POST /v1/media/{media_id}/insight  
UPDATE /v1/media/{media_id}/insights  
UPDATE /v1/media/{media_id}/insight/{insight_type}  
DELETE /v1/media/{media_id}/insights  
DELETE /v1/media/{media_id}/insight/{insight_type}  

### Search capabilities
GET /v1/search/metadata?media_id=X&user_id=X&start_date=X&end_date=  
GET /v1/search/insights?object=X&person=  

### Security
UPDATE /v1/rotate_key

# Deploy


# Development
## Environment

## Build

## Test
