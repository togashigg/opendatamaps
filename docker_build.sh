#!/bin/bash
# docker_build.sh: build docker image.
# Copyright (C) N.Togashi 2023-2026

ARCH="`uname -m`"

echo "`date '+%Y/%m/%d %H:%M:%S'` docker_build.sh start." > ./docker_build.log
echo "CPU architechture=$ARCH" >> ./docker_build.log
cat ./docker_build.log
echo "..."
# clear build directory
if [ -d ./build ]; then
    rm -rf ./build
fi
# make build directory
mkdir ./build
cp -p ./Dockerfile ./Procfile ./manage.py ./requirements.txt ./runtime.txt ./build/
if [ "$ARCH" == "i386" -o "$ARCH" == "i686" ]; then
    sed "s#python:#i386/python:#g" Dockerfile > ./build/Dockerfile
fi
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
cp -pr ./src/*.py ./src/*.json ./build/src/
# build
(cd ./build; docker build -t opendatamaps:latest .) >> ./docker_build.log 2>&1
rc=$?
echo "docker-build ended, rc=$rc" >> ./docker_build.log
# end
echo "`date '+%Y/%m/%d %H:%M:%S'` docker_build.sh ended." >> ./docker_build.log
tail ./docker_build.log
exit $rc

