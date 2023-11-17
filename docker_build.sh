#!/bin/bash
# docker_build.sh: build docker image.
# Copyright (C) N.Togashi 2023

echo "`date '+%Y/%m/%d %H:%M:%S'` docker_build.sh start."
# clear build directory
if [ -d ./build ]; then
    rm -rf ./build
fi
# make build directory
mkdir ./build
cp -p ./Dockerfile ./Procfile ./manage.py ./requirements.txt ./runtime.txt ./build/
# cache directory
mkdir ./build/cache
cp -p ./cache/.dummy ./build/cache/
# djangoapp directory
mkdir ./build/djangoapp
cp -p ./djangoapp/*.py ./build/djangoapp/
mkdir ./build/djangoapp/log
touch ./build/djangoapp/log/django.log
touch ./build/djangoapp/log/djangoapp.log
cp -pr ./djangoapp/static ./build/djangoapp/
cp -pr ./djangoapp/templates ./build/djangoapp/
# download directory
mkdir ./build/download
cp -p ./download/.dummy ./build/download/
cp -p ./download/都道府県コード及び市区町村コード_*.csv ./build/download/
# log directory
mkdir ./build/log
touch ./build/log/crawler.log
touch ./build/log/opendatadb.log
# src directory
mkdir ./build/src
cp -pr ./src/*.py ./build/src/
# build
(cd ./build; docker build -t opendatamaps:latest .) > ./docker_build.log
rc=$?
# end
tail ./docker_build.log
echo "`date '+%Y/%m/%d %H:%M:%S'` docker_build.sh ended, rc=$rc"
exit $rc

