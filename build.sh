#!/bin/bash
repo=iax7
name=testapi
ver=0.8.1

rm -v *.pyc

docker build --build-arg http_proxy="$http_proxy" \
             --build-arg https_proxy="$https_proxy" \
             --build-arg app_version="$ver" \
             -t $repo/$name:$ver .
docker tag $repo/$name:$ver $repo/$name:latest

echo "docker push $repo/$name:$ver"
echo "docker push $repo/$name:latest"
