# Dockerfile for オープンデータ活用
# Copyright (C) N.Togashi 2023
# build: docker build -t opendatamaps:latest .
# run: docker run -d --name opendatamaps -p 80:8080 opendatamaps
# base image
FROM   ubuntu:22.04
MAINTAINER togashigg <KGG03575@nifty.com>
RUN    apt update && apt -y upgrade \
    && apt clean
# タイムゾーン設定
RUN    apt update \
    && apt install -y tzdata \
    && apt clean
ENV    TZ Asia/Tokyo
# 時刻同期
# RUN    apt update \
#     && apt install -y ntp \
#     && cp -p /etc/ntp.conf /etc/ntp.conf.back \
#     && sed -i -e 's/^pool /# pool /g' /etc/ntp.conf \
#     && echo 'server ntp.nict.jp' >> /etc/ntp.conf \
#     && systemctl restart ntp \
#     && apt clean
# 日本語化
RUN    apt update \
    && apt install -y language-pack-ja-base language-pack-ja locales \
    && locale-gen ja_JP.UTF-8 \
    && echo 'LANG=ja_JP.UTF-8' > /etc/default/locale \
    && apt clean
ENV    LANG ja_JP.UTF-8
# Python3パッケージをインストール
RUN    apt update \
    && apt install -y python3 python3-pip \
    && apt clean
# Python3必須ライブラリをインストール
RUN    mkdir /app
WORKDIR /app
ADD    requirements.txt /app/
RUN    pip3 install -r requirements.txt
# アプリケーションをインストール
ADD    . /app/
# Djangoを常駐化
ENTRYPOINT python3 manage.py runserver 0.0.0.0:8080
EXPOSE 8080
