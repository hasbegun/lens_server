CONTAINER_HOME=/home/developer/workspace
IMG_NAME=innox/web:0.1
CONTAINER_NAME=web

docker run -it --rm \
    -p 8080:8080 \
    -v $(pwd)/src:$CONTAINER_HOME/src:rw \
    -v $(pwd)/uploads:$CONTAINER_HOME/uploads:rw \
    --name $CONTAINER_NAME \
    $IMG_NAME