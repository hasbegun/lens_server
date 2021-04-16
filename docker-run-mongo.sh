CONTAINER_MONGO_DB_HOME=/data/db
EXTERNAL_MONO_DB_HOME=mongodb-data
CONTAINER_NAME=mongodb4
IMG_NAME=innox/mongodb:4.4
docker run -it --rm \
    -p 27017:27017 \
    -v $(pwd)/$EXTERNAL_MONO_DB_HOME:$CONTAINER_MONGO_DB_HOME:rw
    --name $CONTAINER_NAME \
    $IMG_NAME