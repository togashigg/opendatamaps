#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# api.py: オープンデータAPIクラス
# Copyright (C) N.Togashi 2023

import os
import sys
import math
import time
import psycopg2
import logging
from src import db

# 定数定義
QUERY_LIMIT = 100
SELECT_LIMIT = 1000

class OpendataMapsApi:

    db = None
    conn = None
    cache_dir = None
    logger = None

    def __init__(self, logname=''):
        if logname == '':
            my_logname = __name__
        else:
            my_logname = logname + '.api'
        self.logger = logging.getLogger(my_logname)
        self.logger.debug('__init__() start.')
        self.db = db.OpendataMapsDb(logname=logname)
        self.conn = self.db.connect()
        self.logger.debug('__init__() ended.')

    def __del__(self):
        self.logger.debug('__del__() start.')
        if self.conn is not None:
            self.db.disconnect()
        self.conn = None
        self.db = None
        self.logger.debug('__del__() ended.')

    def get_opendatamaps_kinds(self, codes):
        """
        opendatamapsテーブルの種別(kind)一覧を取得する。
        :param codes: list型、市区町村コードのリストを指定する。省略する場合はNoneまたは[]を指定する。
        :return: list型、str型種別(kind)のリストを返却する。
        """
        self.logger.debug('get_opendatamaps_kinds() start.')
        rc = None
        sel_dict = {'codes': ''}
        # 検索実行
        sel_sql = "SELECT DISTINCT kind FROM opendatamaps {codes} ORDER BY kind;"
        if codes is not None and codes != []:
            sel_dict['codes'] = 'WHERE '
            adding = '('
            for code in codes:
                sel_dict['codes'] += adding
                if '%' in code:
                    sel_dict['codes'] += "locality_code LIKE '" + code + "'"
                else:
                    sel_dict['codes'] += "LEFT(locality_code," + str(len(code)) + ") = '" + code + "'"
                adding = ' OR '
            if adding != '(':
                sel_dict['codes'] += ")"
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = {'kinds': [rec[0] for rec in recs]}
        self.logger.debug('get_opendatamaps_kinds() ended, rc=' + str(rc))
        return rc

    def get_summary(self):
        """
        opendatamapsとlocalitycodeテーブルからデータ一覧(code,state_name,locality_name,kind,count(*))を取得する。
        :return: list型、レコード(code,state_name,locality_name,kind,count(*))のリストを返却する。
        """
        self.logger.debug('get_summary() start.')
        rc = None
        sel_dict = {'codes': ''}
        # 検索実行
        sql = '''SELECT f.locality_code,f.kind,MAX(c.state_name),MAX(c.locality_name),COUNT(*)
                 FROM opendatamaps f JOIN localitycode c ON f.locality_code = c.code
                 GROUP BY f.locality_code,f.kind ORDER BY f.locality_code,f.kind;'''
        with self.conn.cursor() as cur:
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = []
        code = ''
        for rec in recs:
            if rec[0] != code:
                rc.append({'code': rec[0], 'state_name': rec[2],
                        'locality_name': rec[3], 'kinds': [rec[1]],
                        'kind_count':[rec[4]]})
                code = rec[0]
            else:
                rc[-1]['kinds'].append(rec[1])
                rc[-1]['kind_count'].append(rec[4])
        # self.logger.debug('rc=' + str(rc))
        self.logger.debug('get_summary() ended, len(rc)=' + str(len(rc)))
        return rc

    def get_by_localitycode(self, codes, kinds, limit=QUERY_LIMIT):
        """
        指定した都道府県コードまたｈ市区町村コードおよびデータ種別を含むレコードリストを検索して返却する。
        :param codes: list型、都道府県コードまたｈ市区町村コードを指定する。省略する場合はNoneを指定する。例：['22203','22206']
        :param kinds: list型、データ種別をリストで指定する。省略する場合はNoneを指定する。例：['公衆トイレ']
        :param limit: int型、最大返却数、省略値=100件、0またはNoneを指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリスト
        """
        self.logger.debug('get_by_localitycode() start.')
        rc = None
        sel_dict = {'AND': '', 'codes': '', 'kinds': '', 'limit': ''}
        # 検索実行
        sel_sql = "SELECT * FROM opendatamaps" \
                + " WHERE {codes}{AND}{kinds}{limit};"
        if codes is not None:
            adding = '('
            for code in codes:
                sel_dict['codes'] += adding
                if '%' in code:
                    sel_dict['codes'] += "locality_code LIKE '" + code + "'"
                else:
                    sel_dict['codes'] += "LEFT(locality_code," + str(len(code)) + ") = '" + code + "'"
                adding = ' OR '
            if adding != '(':
                sel_dict['codes'] += ")"
        if kinds is not None:
            in_kinds = [k for k in kinds if k[0] != '!']
            not_in_kinds = [k[1:] for k in kinds if k[0] == '!' and len(k) > 1]
            if len(in_kinds) > 0:
                sel_dict['kinds'] += "kind IN " + "('" + "','".join(in_kinds) + "')"
            if len(not_in_kinds) > 0:
                if sel_dict['kinds'] != '':
                    sel_dict['kinds'] += ' AND '
                sel_dict['kinds'] += "kind NOT IN " + "('" + "','".join(not_in_kinds) + "')"
        if sel_dict['codes'] != '' and sel_dict['kinds'] != '':
            sel_dict['AND'] = ' AND '
        if limit is not None and limit > 0:
            sel_dict['limit'] = " LIMIT " + str(limit)
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = [{'locality_code': rec[0],
               'kind': rec[1],
               'dataset': rec[2],
               'id': rec[3],
               'label': rec[4],
               'lat': rec[5],
               'lng': rec[6],
               'info': rec[7],
               'error': rec[8],
              } for rec in recs]
        self.logger.debug('get_by_localitycode() ended, len(rc)=' + str(len(rc)))
        return rc

    def get_by_distance_from_center(self, c_lat, c_lng, distance, kinds, limit=QUERY_LIMIT):
        """
        中心（緯度・経度）からの距離内に含まれるレコードリストを検索して返却する。
        採用：距離1kmあたりの緯度・経度の度数を計算（日本・北緯35度）　https://easyramble.com/latitude-and-longitude-per-kilometer.html
        参考：Pythonで出発点と進む距離・方向から到着点の緯度経度を計算する方法　https://note.com/calmtree/n/n358d70561b68
        :param c_lat: float型、中心の緯度
        :param c_lng: float型、中心の経度
        :param distance: int型、中心からの距離（m）
        :param kinds: list型、データ種別をリストで指定する。省略する場合はNoneを指定する。例：['公衆トイレ']
        :param limit: int型、最大返却数、省略またはNone指定時は100件。0を指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリスト
        """
        self.logger.debug('get_by_distance_from_center() start.')
        self.logger.debug('c_lat=' + str(c_lat) + ', c_lng=' + str(c_lng) + ', distance=' + str(distance) + ', kinds=' + str(kinds) + ', limit=' + str(limit))
        rc = None
        sel_dict = {'kinds': '', 'limit': SELECT_LIMIT}
        # 中心と距離から検索範囲とする緯度・経度を求める
        POLE_RADIUS = 6356752.314    # 地球の極半径(m)
        lat_degree = 360 / (2 * math.pi * POLE_RADIUS)
        sel_dict['lat_start'] = c_lat - (lat_degree * distance)
        sel_dict['lat_end'] = c_lat + (lat_degree * distance)
        EQUATOR_RADIUS = 6378137    # 地球の赤道半径(m)
        lng_degree = 360 / (2 * math.pi * (EQUATOR_RADIUS * math.cos(c_lat * math.pi / 180.0)))
        sel_dict['lng_start'] = c_lng - (lng_degree * distance)
        sel_dict['lng_end'] = c_lng + (lng_degree * distance)
        # 検索実行
        sel_sql = "SELECT * FROM opendatamaps" \
                + " WHERE lat BETWEEN {lat_start} AND {lat_end} AND lng BETWEEN {lng_start} AND {lng_end}" \
                + " {kinds} LIMIT {limit};"
        if kinds is not None:
            in_kinds = [k for k in kinds if len(k) > 0 and k[0] != '!']
            not_in_kinds = [k[1:] for k in kinds if len(k) > 1 and k[0] == '!']
            if len(in_kinds) > 0:
                sel_dict['kinds'] += "AND kind IN " + "('" + "','".join(in_kinds) + "')"
            if len(not_in_kinds) > 0:
                sel_dict['kinds'] += "AND kind NOT IN " + "('" + "','".join(not_in_kinds) + "')"
        if limit is None:
            limit = QUERY_LIMIT
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = [{'locality_code': rec[0],
               'kind': rec[1],
               'dataset': rec[2],
               'id': rec[3],
               'label': rec[4],
               'lat': rec[5],
               'lng': rec[6],
               'info': rec[7],
               'error': rec[8],
               'distance': self.calc_distance((c_lat,c_lng), (rec[5],rec[6]))
              } for rec in recs]
        # self.logger.debug('rc=' + str(rc))
        # 中心からの距離の近い順にソートする
        rc = [rec for rec in rc if rec['distance'] <= distance]
        rc.sort(key=lambda x: x['distance'])
        if limit > 0 and len(rc) > limit:
            rc = rc[:limit]
        # self.logger.debug('sorted rc=' + str(rc))
        self.logger.debug('get_by_distance_from_center() ended, len(rc)=' + str(len(rc)))
        return rc

    def calc_distance(self, center, target):
        """
        中心から対象までの直線距離を求める。
        :param center: list型、中心の緯度・経度を(lat, lng)で指定する。緯度・経度はfloat型。
        :param target: list型、対象の緯度・経度を(lat, lng)で指定する。緯度・経度はfloat型。
        :return: int型、対象までの直線距離。単位はメートル(m)。
        """
        if center[0] is None or type(center[0]) != float or center[0] == 0.0 \
        or center[1] is None or type(center[1]) != float or center[1] == 0.0 \
        or target[0] is None or type(target[0]) != float or target[0] == 0.0 \
        or target[1] is None or type(target[1]) != float or target[1] == 0.0:
            return 999999999
        return round(math.sqrt(
                math.pow((center[0] - target[0]) * 100000, 2)
                + math.pow((center[1] - target[1]) * 100000, 2)
               ))

    def query_localitycode(self, code, state_name, locality_name, limit=QUERY_LIMIT):
        if code is None:
            return self.get_localitycode_by_name(state_name, locality_name,
                    limit=limit)
        else:
            return self.get_localitycode_by_code(code, limit=limit)

    def get_localitycode_by_code(self, code, limit=QUERY_LIMIT):
        """
        localitycodeテーブルをcodeで検索して結果を返却する。
        :param code: str型、都道府県コードまたは市区町村コード。省略した場合は検索条件としない。
        :param limit: int型、最大返却数、省略またはNone指定時は100件。0を指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリストを返却する。
        """
        self.logger.debug('get_localitycode_by_code() start, code=' + str(code))
        rc = None
        sel_dict = {'WHERE': '', 'limit': ''}
        # 検索実行
        sel_sql = "SELECT * FROM localitycode {WHERE}{limit};"
        if code is not None and code != '':
            if '%' in code:
                sel_dict['WHERE'] = "WHERE code LIKE '" + code + "'"
            else:
                sel_dict['WHERE'] = "WHERE LEFT(code," + str(len(code)) + ") = '" + code + "'"
        if limit is None:
            limit = QUERY_LIMIT
        if limit > 0:
            sel_dict['limit'] = " LIMIT " + str(limit)
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = [{'code': rec[0],
               'state_name': rec[1],
               'locality_name': rec[2]
              } for rec in recs]
        self.logger.debug('get_localitycode_by_code() ended, rc=' + str(len(rc)))
        return rc

    def get_localitycode_by_name(self, state, locality, limit=QUERY_LIMIT):
        """
        localitycodeテーブルをstate_nameおよびlocality_nameで検索して結果を返却する。
        :param state: str型、都道府県名、省略した場合は検索条件としない。
        :param locality: str型、市区町村名、省略した場合は検索条件としない。
        :param limit: int型、最大返却数、省略またはNone指定時は100件。0を指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリストを返却する。
        """
        self.logger.debug('get_localitycode_by_name() start, state=' + str(state) + ', locality=' + str(locality))
        rc = None
        sel_dict = {'WHERE': '', 'AND': '', 'where_state': '', 'where_locality': '', 'limit': ''}
        # 検索実行
        sel_sql = "SELECT * FROM localitycode" \
                + " {WHERE} {where_state}{AND}{where_locality}{limit};"
        if state is not None and state != '':
            if '%' in state:
                sel_dict['where_state'] = "state_name LIKE '" + state + "'"
            else:
                sel_dict['where_state'] = "state_name = '" + state + "'"
        if locality is not None and locality != '':
            if '%' in locality:
                sel_dict['where_locality'] = "locality_name LIKE '" + locality + "'"
            else:
                sel_dict['where_locality'] = "locality_name = '" + locality + "'"
        if sel_dict['where_state'] != '' or sel_dict['where_locality'] != '':
            sel_dict['WHERE'] = 'WHERE'
        if sel_dict['where_state'] != '' and sel_dict['where_locality'] != '':
            sel_dict['AND'] = ' AND '
        if limit is None:
            limit = QUERY_LIMIT
        if limit > 0:
            sel_dict['limit'] = " LIMIT " + str(limit)
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            self.logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            self.logger.debug('select len(recs)=' + str(len(recs)))
            # self.logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に変換する
        rc = [{'code': rec[0],
               'state_name': rec[1],
               'locality_name': rec[2]
              } for rec in recs]
        self.logger.debug('get_localitycode_by_code() ended, rc=' + str(len(rc)))
        return rc

