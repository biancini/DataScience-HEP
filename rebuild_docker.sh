#!/bin/bash

set -ex
IMAGE_NAME="biancini/datascience-hep"
TAG="${1}"

docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest .
docker push ${IMAGE_NAME}:${TAG}
docker push ${IMAGE_NAME}:latest