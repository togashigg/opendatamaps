#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# crawler.py: オープンデータを取得して共通形式でキャッシュする
# Copyright (C) N.Togashi 2023

import os
import sys
import time
import re
import csv
import json
import pathlib
import requests
import chardet
import unicodedata
import logging

class Crawler:

    APP_DIR = None
    index_path = None
    index = None
    common = None
    state = None        # 都道府県名
    name = None         # 市区町村名
    code = None         # 市区町村コード
    names = []
    download_dir = None
    cache_dir = None
    __data_name_dict = {}
    __requests_retry_max = 3
    __request_headers = {}
    __proxies = {}
    __geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={address}&language=ja&components=country:JP&key={key}'
    __google_maps_api_key = 'AIzaSyBZa9fI3N-L1OHnkiaGQODmOcPRP-HaWlA'
    __geocode_cache = None
    __geocode_cache_file = '.geocode_cache_{}.json'
    __geocode_cache_path = None
    __geocode_cache_update = False

    def __init__(self, index_path):
        """
        コンストラクタ
        :param index_path: index.jsonファイルのパス
        :return: なし
        :raise: Exceltion
        """
        logger = logging.getLogger(__name__)
        logger.debug('__init__() start, index_path=' + str(index_path))
        self.APP_DIR=os.path.join(BASE_DIR, 'djangoapp')
        self.index_path = index_path
        if self.index_path == None or self.index_path == '':
            self.index_path = os.path.join(self.APP_DIR, 'crawler', 'index.json')
            logger.debug('default index_path='+self.index_path)
        if not os.path.exists(self.index_path):
            raise Exception('index_path not exists, ' + self.index_path)
        try:
            self.index = json.loads(open(self.index_path, 'r').read())
        except Exception as e:
            logger.exception(e)
            raise Exception('error in index_path at open or load json, '
                    + self.index_path)
        # logger.debug('index='+json.dumps(self.index, ensure_ascii=False))
        self.common = self.index['common']
        logger.debug('common=' + json.dumps(self.common, ensure_ascii=False))
        self.names = [v['name'] for v in self.index['list']]
        logger.debug('names=' + str(self.names))
        # download_dirの確認
        self.download_dir = os.path.join(self.APP_DIR, self.common['download_dir'])
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logger.info('makedirs download_dir ' + self.download_dir)
        # cache_dirの確認
        self.cache_dir = os.path.join(self.APP_DIR, self.common['cache_dir'])
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info('makedirs cache_dir ' + self.cache_dir)
        logger.debug('__init__() ended.')
        # 復帰
        return

    def __del__(self):
        """
        デストラクタ
        :return: なし
        """
        logger = logging.getLogger(__name__)
        logger.debug('__del__() start.')
        pass
        logger.debug('__del__() ended.')
        return

    def get_names(self):
        """
        """
        logger = logging.getLogger(__name__)
        logger.debug('get_names() start.')
        # 復帰
        logger.debug('get_names() ended, rc=' + str(self.names))
        return self.names

    def make_cache_data(self, name):
        """
        指定された自治体のオープンデータを取得しマッピング形式に変換してキャッシュする
        :param name: str型、自治体名
        :return: なし
        :raise: Exception
        """
        logger = logging.getLogger(__name__)
        logger.debug('make_cache_data() start, name=' + str(name))
        # 実行
        rc = 0
        try:
            # 自治体名の定義確認
            self.name = name
            if self.name not in self.names:
                raise Exception('name not exists in index, ' + self.name)
            self.state = [v['state'] for v in self.index['list'] if v['name']==self.name][0]
            self.code = [v['code'] for v in self.index['list'] if v['name']==self.name][0]
            logger.debug('code=' + self.code)
            # download_dirを設定
            self.download_dir = os.path.join(self.APP_DIR,
                    self.common['download_dir'],
                    self.common['dir_name'].format(
                            code=self.code, name=self.state+self.name))
            if not os.path.exists(self.download_dir):
                # raise Exception('download_dir not exists, ' + self.download_dir)
                os.mkdir(self.download_dir)
                logger.info('mkdir download_dir ' + self.download_dir)
            logger.debug('download_dir=' + self.download_dir)
            # cache_dirを設定
            self.cache_dir = os.path.join(self.APP_DIR,
                    self.common['cache_dir'],
                    self.common['dir_name'].format(
                            code=self.code, name=self.state+self.name))
            if not os.path.exists(self.cache_dir):
                # raise Exception('cache_dir not exists, ' + self.cache_dir)
                os.mkdir(self.cache_dir)
                logger.info('mkdir cache_dir ' + self.cache_dir)
            logger.debug('cache_dir=' + self.cache_dir)
            # geocode検索結果キャッシュを初期化
            self.__geocode_cache = {}
            self.__geocode_cache_update = False
            self.__geocode_cache_path = os.path.join(self.cache_dir, self.__geocode_cache_file.format(name))
            if os.path.exists(self.__geocode_cache_path):
                self.__geocode_cache = json.loads(open(self.__geocode_cache_path, 'r').read())
            # 情報一覧取得
            titles = [y['title'] for x in self.index['list'] if x['name']==self.name for y in x['data']]
            logger.debug('titles=' + str(titles))

            info_list = [v['data'] for v in self.index['list'] if v['name']==self.name][0]
            for info in info_list:
                file = info['url'].split('/')[-1]
                file_cache = str(pathlib.Path(file).with_suffix('.json'))
                if self.exists_in_cache(file_cache):
                    msg = info['title'] + '：' + file_cache + ' 取得済'
                    logger.info(msg)
                    print(msg, file=sys.stderr)
                else:
                    msg = info['title'] + '：' + file + ' 取得開始'
                    logger.info(msg)
                    print(msg, file=sys.stderr, end=' ... ')
                    content = self.url_get(info['url'], file)
                    print('変換開始', file=sys.stderr, end=' ... ')
                    content = self.convert_to_utf8(content)
                    map_data = self.convert_to_mapping_data(content, info)
                    print('保存開始', file=sys.stderr, end=' ... ')
                    self.save_to_cache(map_data, file_cache)
                    logger.info(info['title'] + ' 取得完了')
                    print('取得完了', file=sys.stderr)
        except Exception as e:
            logger.exception(e)
            rc = 99
        # geocode検索結果キャッシュを保存
        if self.__geocode_cache_update:
            cache_json = json.dumps(self.__geocode_cache, ensure_ascii=False).replace('"OK"}, "', '"OK"},\n"')
            with open(self.__geocode_cache_path, 'w') as h_cache:
                h_cache.write(cache_json)
        # 復帰
        logger.debug('make_cache_data() ended, rc=' + str(rc))
        return rc

    def url_get(self, url, file, cache=True):
        """
        指定されたURLの内容を取得してdownload_dirに保存する
        :param url: str型、取得する資源のURL
        :param file: str型、URLのファイル名部分
        :param cache: boolean型、True=キャッシュを使用する、False:キャッシュを使用しない
        :return: str型、取得したコンテンツ
        :raise: Exception
        """
        logger = logging.getLogger(__name__)
        logger.debug('url_get() start, url=' + url + ', file=' + str(file))
        # 実行
        if cache \
        and os.path.exists(os.path.join(self.download_dir, file)):
            # キャッシュから読み込む
            content = open(os.path.join(self.download_dir, file), 'rb').read()
        else:
            # HTTP GET
            content = None
            for try_i in range(self.__requests_retry_max):
                try_ok = False
                try:
                    res = requests.get(url, headers=self.__request_headers, proxies=self.__proxies)
                    try_ok = True
                except requests.exceptions.ProxyError as e:
                    logger.exception(e)
                    res = None
                    if (try_i+1) < self.__requests_retry_max:
                        time.sleep(self.__requests_retry_seconds)
                if try_ok:
                    break
            if res is None or res.status_code != requests.codes.ok:
                logger.error('requests error(2): ' + str(res))
            else:
                logger.debug('response.encoding: ' + str(res.encoding))
                content = res.content
            if res is not None:
                res.close()
            # download_dirに保存する
            if cache:
                self.__save_to_download_dir(content, file)

        # 復帰
        logger.debug('url_get() ended, file=' + str(file))
        return content

    def convert_to_utf8(self, content):
        """
        """
        logger = logging.getLogger(__name__)
        logger.debug('convert_to_utf8() start.')
        # 実行
        detect = {'encoding': 'UTF-8', 'confidence': 0.5, 'language': 'Japanese'}
        try:
            detect = chardet.detect(content)
        except Exception as e:
            logger.exception(e)
        logger.debug(str(detect))
        if detect['encoding'] is None:
            detect['encoding'] = 'CP932'
        data = content.decode(detect['encoding'])
        # 復帰
        logger.debug('convert_to_utf8() ended.')
        return data

    def convert_to_mapping_data(self, content, info):
        """
        """
        logger = logging.getLogger(__name__)
        logger.debug('convert_to_mapping_data() start.')
        data = None
        if info['format'] == 'CSV':
            data = self.data_from_csv(content, info);
        elif info['format'] == 'TSV':
            data = self.data_from_tsv(content, info);
        # 復帰
        logger.debug('convert_to_mapping_data() ended.')
        return data

    def data_from_csv(self, content, info):
        """
        CSV形式のデータをJSON形式に変換する。
        :param content: str型、CSV形式文字列
        :param info: dict型、形式情報
        :return: str型、JSON形式データ
        """
        logger = logging.getLogger(__name__)
        logger.debug('data_from_csv() start.')
        # 実行
        data = [v for v in csv.reader(content.replace('\r', '').split('\n'))]
        map_data = []
        headers = []
        if 'address' not in info:
            info['address'] = -1
        self.__data_name_dict = {}
        for i, rec in enumerate(data):
            if i >= info['header'] and len(rec) > 0 \
            and rec[0] != '' and rec[0][0] != '#' \
            and len(rec) > info['name']:
                if rec[info['name']] in self.__data_name_dict:
                    self.__data_name_dict[rec[info['name']]] += 1
                else:
                    self.__data_name_dict[rec[info['name']]] = 1
        no = 0;
        for i in range(len(data)):
            if len(data[i]) == 0 or len(data[i][0]) == 0:
                continue;
            if data[i][0][0] == '#':
                continue;
            if i < info['header']:
                headers = data[i]
                if info['address'] == -1:
                    if '住所' in headers:
                        info['address'] = headers.index('住所')
                    elif '所在地' in headers:
                        info['address'] = headers.index('所在地')
                    else:
                        info['address'] =  -1
                continue;
            if info['name'] == '' or data[i][info['name']] == '':
                continue;
            label = ''
            if 'label' in info:
                for j in info['label']:
                    if type(j) == int:
                        label += data[i][j]
                    else:
                        label += str(j)
            else:
                label = data[i][info['name']]
            info_items = {}
            for j in info['info']:
                if data[i][j] == '':
                    continue
                info_items['item'+('0'+str(j))[-2:]] = {'key': headers[j], 'value': data[i][j]}
            error = ''
            no += 1
            id_value = ('000' + str(no))[-4:]
            if info['id'] >= 0:
                if data[i][info['id']] != '':
                    id_value = data[i][info['id']]
            else:
                error += 'id未設定。'
            address = ''
            if info['address'] >= 0 and info['address'] < len(data[i]):
                address = data[i][info['address']]
            (lat, lng, msg) = self.lat_lng_from_data(data[i], info, address)
            data_value = {
                    "id": id_value,
                    "locality_code": self.code,
                    "locality_name": self.state + self.name,
                    "kind": info['kind'],
                    "label": label,
                    "lat": lat,
                    "lng": lng,
                    "info": info_items,
            }
            if msg != '':
                data_value["error"] = msg
            map_data.append(data_value)
        self.__data_name_dict = {}
        # 復帰
        logger.debug('data_from_csv() ended.')
        return map_data

    def data_from_tsv(self, content, info):
        """
        """
        logger = logging.getLogger(__name__)
        logger.debug('data_from_tsv() start.')
        # 実行
        data = [v for v in csv.reader(content.replace('\r', '').split('\n'),
                delimiter='\t', quotechar=None)]
        map_data = []
        headers = []
        if 'address' not in info:
            info['address'] = -1
        no = 0;
        if data[0][0] == '#LINK':
            # LinkTable形式
            logger.debug('#LINK形式')
            for i in range(len(data)):
                if len(data[i]) == 0 or len(data[i][0]) == 0:
                    continue;
                if data[i][0] == '#property':
                    headers = ['id'] + data[i][1:]
                    continue
                if data[i][0][0] == '#':
                    continue;
                if info['name'] == '' or data[i][info['name']] == '':
                    continue;
                info_items = {}
                for j in info['info']:
                    if data[i][j] == '':
                        continue
                    info_items['item'+('0'+str(j))[-2:]] = {'key': headers[j], 'value': data[i][j]}
                no += 1
                id_value = ('000' + str(no))[-4]
                if info['id'] >= 0:
                    id_value = data[i][info['id']];
                label = ''
                if 'label' in info:
                    for j in info['label']:
                        if type(j) == int:
                            label += data[i][j]
                        else:
                            label += str(j)
                else:
                    label = data[i][info['name']]
                address = ''
                if info['address'] >= 0 and info['address'] < len(data[i]):
                    address = data[i][info['address']]
                (lat, lng, msg) = self.lat_lng_from_data(data[i], info, address)
                data_value = {
                        "id": id_value,
                        "locality_code": self.code,
                        "locality_name": self.state + self.name,
                        "kind": info['kind'],
                        "label": label,
                        "lat": lat,
                        "lng": lng,
                        "info": info_items,
                }
                if msg != '':
                    data_value["error"] = msg
                map_data.append(data_value)
        else:
            for i in range(len(data)):
                if len(data[i]) == 0 or len(data[i][0]) == 0:
                    continue;
                if data[i][0][0] == '#':
                    continue;
                if i < info['header']:
                    headers = data[i]
                    continue;
                if data[i][info['name']] == '':
                    continue;
                info_items = {}
                for j in info['info']:
                    if data[i][j] == '':
                        continue
                    info_items['item'+('0'+str(j))[-2:]] = {'key': headers[j], 'value': data[i][j]}
                no += 1
                id_value = ('000' + str(no))[-4]
                if info['id'] >= 0:
                    id_value = data[i][info['id']];
                label = ''
                if 'label' in info:
                    for j in info['label']:
                        if type(j) == int:
                            label += data[i][j]
                        else:
                            label += str(j)
                else:
                    label = data[i][info['name']]
                address = ''
                if info['address'] >= 0 and info['address'] < len(data[i]):
                    address = data[i][info['address']]
                (lat, lng, msg) = self.lat_lng_from_data(data[i], info, address)
                data_value = {
                        "id": id_value,
                        "locality_code": self.code,
                        "locality_name": self.state + self.name,
                        "kind": info['kind'],
                        "label": label,
                        "lat": lat,
                        "lng": lng,
                        "info": info_items,
                }
                if msg != '':
                    data_value["error"] = msg
                map_data.append(data_value)
        # 復帰
        logger.debug('data_from_tsv() ended.')
        return map_data

    def exists_in_cache(self, file):
        """
        指定されたファイルがキャッシュに存在するか確認する
        :param file: str型、ファイル名
        :return: boolean型、True=存在する、False=存在しない
        """
        logger = logging.getLogger(__name__)
        logger.debug('exists_in_cache() start, file=' + str(file))
        # 実行
        rc = False
        if os.path.exists(os.path.join(self.cache_dir, file)):
            rc = True
        # 復帰
        logger.debug('exists_in_cache() ended, rc=' + str(rc))
        return rc

    def save_to_cache(self, mapping_data, file):
        """
        """
        logger = logging.getLogger(__name__)
        logger.debug('save_to_cache() start, file=' + file)
        # 実行
        try:
            content = json.dumps(mapping_data, ensure_ascii=False).replace('}, {', '},\n{')
            with open(os.path.join(self.cache_dir, file), 'w') as f:
                f.write(content)
        except Exception as e:
            logger.exception(e)
            raise Exception('error in store_to_download_dir(), file=' + file)
        # 復帰
        logger.debug('save_to_cache() ended, file=' + str(file))
        return content

    def __save_to_download_dir(self, content, file):
        """
        contentをdownload_dirにファイルとして保存する
        :param content: byte型、ファイルの内容
        :param file: str型、ファイル名
        :return: boolean型、True=正常終了
        :raise Exception: 異常終了
        """
        logger = logging.getLogger(__name__)
        logger.debug('__save_to_download_dir() start, file=' + file)
        logger.debug('save file=' + os.path.join(self.download_dir, file))
        # 実行
        try:
            with open(os.path.join(self.download_dir, file), 'wb') as f:
                f.write(content)
        except Exception as e:
            logger.exception(e)
            raise Exception('error in store_to_download_dir().')
        # 復帰
        logger.debug('__save_to_download_dir() ended.')
        return True

    def lat_lng_from_data(self, data, info, address):
        """
        レコードの緯度・経度を浮動小数点形式で返却する。
        緯度・経度が設定されていない場合は、名称または住所から緯度・経度を求める。
        :param data: Array型、データレコード
        :param info: dict型、データ定義
        :param address: str型、住所
        :return: (緯度, 経度, メッセージ)、緯度=float型、経度=float型、メッセージ=str型
        """
        logger = logging.getLogger(__name__)
        logger.debug('lat_lng_from_data() start, data=' + str(data) + ', info=' + str(info))
        # 実行
        lat = ''
        lng = ''
        msg = ''
        if data[info['name']] in self.__data_name_dict \
        and self.__data_name_dict[data[info['name']]] > 1:
            msg += '名称が重複。'
        if info['lat'] == -1 or info['lng'] == -1:
            msg += '緯度・経度が未定義。'
        elif data[info['lat']] == '' or data[info['lng']] == '':
            msg += '緯度・経度が未設定。'
        else:
            lat = data[info['lat']]
            lng = data[info['lng']]
        if lat == '' or lng == '':
            # 名称から緯度・経度を取得する
            param_addr = self.state + self.name + ' ' + data[info['name']]
            if param_addr in self.__geocode_cache:
                result = self.__geocode_cache[param_addr]
                logger.debug('Hit in cache, 名称=' + param_addr)
            else:
                geo_url = self.__geocode_url.format(address=param_addr, key=self.__google_maps_api_key)
                content = self.url_get(geo_url, None, cache=False)
                result = json.loads(content)
                self.__geocode_cache[param_addr] = result
                self.__geocode_cache_update = True
            logger.debug(param_addr + '：' + str(result))
            if result['status'] == 'OK':
                for res in result['results']:
                    if 'geometry' in res:
                        if 'location_type' in res['geometry']:
                            if self.state + self.name not in res['formatted_address']:
                                continue
                            if res['geometry']['location_type'] == 'ROOFTOP':
                                lat = res['geometry']['location']['lat']
                                lng = res['geometry']['location']['lng']
                                msg += '名称から緯度・経度を取得1(' + res['geometry']['location_type']
                                if unicodedata.normalize('NFKC', res['address_components'][0]['long_name']) \
                                         == unicodedata.normalize('NFKC', data[info['name']]):
                                    msg += ')。'
                                else:
                                    msg += ')=' + res['formatted_address'] + '。'
                                    break
                            elif res['geometry']['location_type'] == 'GEOMETRIC_CENTER':
                                if res['address_components'][0]['long_name'] == data[info['name']]:
                                    lat = res['geometry']['location']['lat']
                                    lng = res['geometry']['location']['lng']
                                    msg += '名称から緯度・経度を取得2(' + res['geometry']['location_type'] + ')。'
                                    break
                                elif len(result['results']) == 1 and address == '' \
                                and (res['address_components'][0]['long_name'][:2] == data[info['name']][:2] \
                                  or res['address_components'][0]['long_name'][-2:] == data[info['name']][-2:]):
                                    lat = res['geometry']['location']['lat']
                                    lng = res['geometry']['location']['lng']
                                    msg += '名称（類似）から緯度・経度を取得3(' + res['geometry']['location_type']
                                    if unicodedata.normalize('NFKC', res['address_components'][0]['long_name']) \
                                             == unicodedata.normalize('NFKC', data[info['name']]):
                                        msg += ')。'
                                    else:
                                        msg += ')=' + res['formatted_address'] + '。'
                                    msg += '住所未設定。'
                                    break
                            elif address != '':
                                a_addr = unicodedata.normalize('NFKC', address.replace('番地', '−'))
                                # logger.debug('a_addr=' + a_addr)
                                a_match = re.match('[^0-9０-９]*([0-9０-９\-−－ー]*)$', a_addr)
                                if a_match is not None and a_match.group(1) != '':
                                    # logger.debug(str(a_match.groups()))
                                    r_addr = unicodedata.normalize('NFKC', res['formatted_address'].replace('番地', '−'))
                                    # logger.debug('r_addr=' + r_addr)
                                    r_match = re.match('[^0-9０-９]*([0-9０-９\-−－ー]*)$', r_addr)
                                    if r_match is not None and r_match.group(1) != '':
                                        if a_match.group(1) == r_match.group(1):
                                            lat = res['geometry']['location']['lat']
                                            lng = res['geometry']['location']['lng']
                                            msg += '名称から緯度・経度を取得4(' + res['geometry']['location_type'] + ')'
                                            msg += '=番地が同一(' + a_match.group(1) + ')。'
                                            break
                            elif address == '' and len(result['results']) == 1:
                                if self.state + self.name in res['formatted_address']:
                                    lat = res['geometry']['location']['lat']
                                    lng = res['geometry']['location']['lng']
                                    msg += '名称から近隣の緯度・経度を取得5(' + res['geometry']['location_type'] \
                                         + ')=' + res['formatted_address'] + '。'
                                    msg += '住所未設定。'
                                    break
                            else:
                                msg += '名称：' + param_addr + '：NG location_type=' + res['geometry']['location_type'] + '。'
                        else:
                            msg += '名称：' + param_addr + '：NG location_type無し。'
                    else:
                        msg += '名称：' + param_addr + '：NG geometry無し。'
            else:
                msg += '名称：' + param_addr + '：NG status=' + result['status'] + '。'
        if lat == '' or lng == '':
            msg += '名称から取得できず。'
            # 住所から緯度・経度を取得する
            if address == '':
                msg += '住所未設定。'
            else:
                param_addr = self.state + address
                if address[:3] != self.name:
                    param_addr = self.state + self.name + address
                if param_addr in self.__geocode_cache:
                    result = self.__geocode_cache[param_addr]
                    logger.debug('Hit in cache, 住所=' + param_addr)
                else:
                    geo_url = self.__geocode_url.format(address=param_addr, key=self.__google_maps_api_key)
                    content = self.url_get(geo_url, None, cache=False)
                    result = json.loads(content)
                    self.__geocode_cache[param_addr] = result
                    self.__geocode_cache_update = True
                logger.debug(param_addr + '：' + str(result))
                if result['status'] == 'OK':
                    if len(result['results']) == 1:
                        res = result['results'][0]
                        if 'location_type' in res['geometry']:
                            # if res['geometry']['location_type'] \
                            #       in ['ROOFTOP', 'RANGE_INTERPOLATED', 'GEOMETRIC_CENTER', 'APPROXIMATE']:
                            if self.state + self.name in res['formatted_address']:
                                lat = res['geometry']['location']['lat']
                                lng = res['geometry']['location']['lng']
                                if res['geometry']['location_type'] == 'ROOFTOP':
                                    msg += '住所から緯度・経度を取得(' + res['geometry']['location_type'] + ')。'
                                else:
                                    msg += '住所から近隣の緯度・経度を取得(' + res['geometry']['location_type']
                                    msg += ')=' + res['formatted_address'] + '。'
                        else:
                            msg += '住所：' + param_addr + '：NG geometry無し。'
                    else:
                        msg += '住所：' + param_addr + '：NG 複数results。'
                else:
                    msg += '住所：' + param_addr + '：NG status=' + result['status'] + '。'
        if (lat == '' or lng == '') and address != '':
            msg += '住所から取得できず。'
        # 浮動小数点形式に変換する
        if type(lat) != float:
            (lat, m) = self.string_to_float(lat)
            if m != '':
                msg += '緯度：' + m
        if type(lng) != float:
            (lng, m) = self.string_to_float(lng)
            if m != '':
                msg += '経度：' + m
        # 復帰
        logger.debug('lat_lng_from_data() ended, lat=' + str(lat) + ', lng=' + str(lng) + ', msg=' + msg)
        return (lat, lng, msg)

    def string_to_float(self, v_str):
        """
        文字列形式の緯度・経度を浮動小数点に変換する
        :param v_str: str型、文字列形式の緯度または経度
        :return: 浮動小数点形式の緯度または経度。ただし、文字列形式の値が空文字の場合は空文字を返却する
        """
        msg = ''
        msg_correct = ''
        v_float = ''
        try:
            if v_str != '':
                v_strs = v_str.split('.')
                if len(v_strs) == 2:
                    # 正しい形式
                    v_float = float(v_str)
                elif len(v_strs) == 1:
                    # 「.」を入れ忘れた？
                    if v_strs[0][0] == '1':
                        v_float = float(v_strs[0][:3] + '.' + v_strs[0][3:])
                    else:
                        v_float = float(v_strs[0][:2] + '.' + v_strs[0][2:])
                    msg += '度に小数点無し。'
                else:
                    # 度.分.秒形式？、日本測地系から世界測地系に簡易補正
                    v_float = float(v_strs[0]) \
                            + float(v_strs[1]) / 60.0
                    msg += '度.分.秒形式から変換'
                    if len(v_strs) >= 3:
                        if len(v_strs) == 3:
                            v_float += float(v_strs[2]) / 3600.0
                        else:
                            v_float += float(v_strs[2]+'.'+v_strs[3]) / 3600.0
                        # 沼津市地点での簡易補正（秒の指定が無ければ誤差の範囲とみなす）
                        if v_float > 90.0:
                            v_float -= 11.29 / 3600
                            msg_correct = '-11.29秒'
                        else:
                            v_float += 11.85 / 3600
                            msg_correct = '+11.85秒'
                        msg += '・簡易補正'
                    msg += '(' + v_str + msg_correct + ')。'
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return (v_float, msg)

def setup_logger(name, level, log_file='crawler.log', log_dir='log'):
    """
    コマンド実行時のログ初期化
    :param name: str型、関数、__main__
    :param level: int型、logging.INFO、logging.DEBUG、...
    :param log_file: str型/stderr、ログファイル名またはstderr
    :param log_dir: str型、ログディレクトリ名、log_fileがログファイル名の場合に有効なパラメタ
    :return: logger
    """
    logger = logging.getLogger(name)
    logger.parent.setLevel(level)
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_handler_format = logging.Formatter(log_format)
    if type(log_file) is str:
        # ファイル出力ハンドラ
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
        # log_file_handler= logging.handlers.RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=1024000, backupCount=5)
        log_file_handler.setLevel(level)
        log_file_handler.setFormatter(log_handler_format)
        logger.addHandler(log_file_handler)
    else:
        # 標準エラー出力ハンドラ
        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setLevel(level)
        log_stream_handler.setFormatter(log_handler_format)
        logger.addHandler(log_stream_handler)
    return logger

# コマンド呼び出し
if __name__ == '__main__':
    # 初期化
    rc = 0
    logger = setup_logger(__name__, logging.DEBUG)  # logging.INFO
    # 実行
    try:
        # パラメタチェック
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument('-l', '--locality_list', action='store_true', help='定義されている自治体名を出力する。')
        p.add_argument('names', nargs='*', type=str, help='自治体名を指定する。')
        args = p.parse_args(sys.argv[1:])
        names = args.names
        # 開始
        msg = 'crawler.py start.'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # 取得開始
        BASE_DIR=os.path.join(os.environ['HOME'], 'github', 'opendatamaps')
        cobj = Crawler(None)
        names_all = cobj.get_names()
        if args.locality_list:
            print('定義済自治体名：' + str(names_all), file=sys.stderr)
            cobj = None
            sys.exit(0)

        if len(names) == 0:
            names = names_all
        for name in names:
            if name not in names_all:
                raise Exception('指定された自治体名が存在しません。' + str(name))
            print('【' + name + '】', file=sys.stderr)
            rc = cobj.make_cache_data(name)
            if rc != 0:
                break
        cobj = None
    except Exception as e:
        logger.exception(e)
        print('', file=sys.stderr)
        rc = 99
    # 終了
    msg = 'crawler.py ended, rc=' + str(rc)
    logger.info(msg)
    print(msg, file=sys.stderr)

    # 復帰
    sys.exit(rc)
