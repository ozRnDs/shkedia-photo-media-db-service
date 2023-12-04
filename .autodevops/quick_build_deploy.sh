cz bump -ch

export MEDIA_DB_SERVICE_VERSION=$(cz version -p)
export IMAGE_NAME=media-db-service:${MEDIA_DB_SERVICE_VERSION}
export IMAGE_FULL_NAME=public.ecr.aws/q2n5r5e8/project-shkedia/${IMAGE_NAME}

docker build . -t ${IMAGE_FULL_NAME}

# export ENVIRONMENT=dev
# export MEDIA_DB_ENV=.local/media_db_service_${ENVIRONMENT}.env
# docker compose --env-file ${MEDIA_DB_ENV} up -d