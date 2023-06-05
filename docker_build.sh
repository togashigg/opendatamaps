#!/bin/bash
# docker_build.sh: build docker image.
# Copyright (C) N.Togashi 2023

# clear build directory
if [ -d ./build ]; then
    rm -rf ./build
fi
# make build directory
mkdir ./build
cp -p ./Dockerfile ./Procfile ./manage.py ./requirements.txt ./runtime.txt ./build/
mkdir ./build/djangoapp
cp -p ./djangoapp/*.py ./build/djangoapp/
mkdir ./build/djangoapp/cache
touch ./build/djangoapp/cache/.dummy
mkdir ./build/djangoapp/crawler
cp -p ./djangoapp/crawler/*.py ./build/djangoapp/crawler/
cp -p ./djangoapp/crawler/*.csv ./build/djangoapp/crawler/
mkdir ./build/djangoapp/crawler/log
touch ./build/djangoapp/crawler/log/crawler.log
touch ./build/djangoapp/crawler/log/opendatadb.log
mkdir ./build/djangoapp/download
touch ./build/djangoapp/download/.dummy
mkdir ./build/djangoapp/log
touch ./build/djangoapp/log/django.log
touch ./build/djangoapp/log/djangoapp.log
cp -pr ./djangoapp/static ./build/djangoapp/
cp -pr ./djangoapp/templates ./build/djangoapp/
# build
(cd ./build; docker build -t opendatamaps:latest .) > ./docker_build.log
rc=$?
# end
echo rc=$rc
exit $rc

