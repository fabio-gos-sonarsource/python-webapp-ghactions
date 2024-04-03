#!/bin/sh

DC_VERSION="latest"
DC_DIRECTORY="."
DC_PROJECT="dependency-check scan: $(pwd)"
DATA_DIRECTORY="$DC_DIRECTORY/.owasp-dependency-check/data"
CACHE_DIRECTORY="$DC_DIRECTORY/.owasp-dependency-check/data/cache"
WORKING_DIRECTORY="$(pwd)"

if [ ! -d "$DATA_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $DATA_DIRECTORY"
    mkdir -p "$DATA_DIRECTORY"
fi
if [ ! -d "$CACHE_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $CACHE_DIRECTORY"
    mkdir -p "$CACHE_DIRECTORY"
fi

# Make sure we are using the latest version
docker pull owasp/dependency-check:$DC_VERSION

docker run --rm \
    --platform="linux/amd64" \
    -e user=joshua \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    --volume $WORKING_DIRECTORY:/src:z \
    --volume "$DATA_DIRECTORY":/usr/share/dependency-check/data:z \
    --volume $WORKING_DIRECTORY/.owasp-dependency-check/odc-reports:/report:z \
    owasp/dependency-check:$DC_VERSION \
    --scan /src \
    --format "ALL" \
    --project "$DC_PROJECT" \
    --out /report 
    
    # Use suppression like this: (where /src == $pwd)
    # --suppression "/src/security/dependency-check-suppression.xml"
