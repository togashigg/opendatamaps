# Dockerfile for オープンデータMaps API、サンプルアプリ実行環境
# Copyright (C) N.Togashi 2023
# build: docker build -t opendatamaps:latest .
# run: docker run -d --name opendatamaps -p 80:8080 \
#             -e GOOGLE_MAPS_API_KEY -e POSTGRESQL_HOST \
#             -e POSTGRESQL_PORT -e POSTGRESQL_DBNAME \
#             -e POSTGRESQL_USER -e POSTGRESQL_PASS \
#             opendatamaps
# base image
# FROM   ubuntu:22.04
FROM   python:3.10-slim
MAINTAINER togashigg <KGG03575@nifty.com>
RUN    apt-get update && apt-get -y upgrade \
    && apt-get clean
# タイムゾーン設定
RUN    apt-get update \
    && apt-get install -y tzdata \
    && apt-get clean
ENV    TZ Asia/Tokyo
# 時刻同期
# RUN    apt-get update \
#     && apt-get install -y ntp \
#     && cp -p /etc/ntp.conf /etc/ntp.conf.back \
#     && sed -i -e 's/^pool /# pool /g' /etc/ntp.conf \
#     && echo 'server ntp.nict.jp' >> /etc/ntp.conf \
#     && systemctl restart ntp \
#     && apt-get clean
# 日本語化
RUN    apt-get update \
    && apt-get install -y locales \
    && locale-gen ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale \
    && apt-get clean
ENV    LANG ja_JP.UTF-8
# Python3パッケージをインストール
RUN    pip3 install --upgrade pip
# Python3必須ライブラリをインストール
RUN    mkdir /app
WORKDIR /app
ADD    requirements.txt /app/
RUN    pip3 install -r requirements.txt
# アプリケーションをインストール
ADD    . /app/
# Djangoを常駐化
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8080 --insecure
EXPOSE 8080
