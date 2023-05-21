#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# opendatadb.py: オープンデータDBの処理クラス
# Copyright (C) N.Togashi 2023
# 結果確認方法：$ psql -h xxx -U xxx -p xxx
#               opendatadb=>\d opendata

import os
import sys
import csv
import json
import math
import time
import psycopg2
import logging

# 定数定義
QUERY_LIMIT = 100
SELECT_LIMIT = 1000

class opendatadb:

    HOST = 'dpg-cgh4qtndvk4ml9sj50h0-a.oregon-postgres.render.com'
    PORT = '5432'
    DBNAME = 'opendatadb'
    USER = 'opendatadb_user'
    PSW = '6Zfdtt5Y9YuZjp210BOahqBpJF1XCPVz'
    COMMIT_COUNT = 100
    LOCALITYCODE_CSV = '都道府県コード及び市区町村コード_20190501.csv'
    conn = None
    cache_dir = None

    def __init__(self):
        if 'BASE_DIR' not in locals():
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.cache_dir = os.path.join(BASE_DIR, 'djangoapp' , 'cache')

    def connect(self):
        logger = logging.getLogger(__name__)
        logger.debug('connect() start.')
        # PostgreSQLサーバへ接続
        if self.conn is None:
            self.conn = psycopg2.connect('host='+self.HOST+' port='+self.PORT+' dbname='+self.DBNAME+' user='+self.USER+' password='+self.PSW)
            logger.debug('connected.')
        logger.debug('connect() ended.')
        return True

    def disconnect(self):
        logger = logging.getLogger(__name__)
        logger.debug('disconnect() start.')
        # 接続を閉じる
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logger.debug('disconnected.')
        logger.debug('disconnect() ended.')
        return True

    def create_tables(self, tables):
        logger = logging.getLogger(__name__)
        logger.debug('create_tables() start, tables=' + str(tables))
        if 'localitycode' in tables:
            self.create_localitycode();
        if 'opendatamaps' in tables:
            self.create_opendatamaps();
        logger.debug('create_tables() ended.')
        return True

    def create_localitycode(self):
        logger = logging.getLogger(__name__)
        logger.debug('create_localitycode() start.')
        # カーソルを取得
        with self.conn.cursor() as cur:
            # localitycodeテーブル作成する
            sql = '''CREATE TABLE localitycode (
                      code           CHAR(6) NOT NULL,
                      state_name     VARCHAR(30) NOT NULL,
                      locality_name  VARCHAR(30),
                      state_yomi     VARCHAR(30) NOT NULL,
                      locality_yomi  VARCHAR(30),
                      CONSTRAINT localitycode_pkey PRIMARY KEY (code)
                  );
                  '''
            # SQL実行
            cur.execute(sql)
            cur.close()
            logger.debug('TABLE(localitycode) created.')
        self.conn.commit()
        logger.debug('commited.')
        logger.debug('create_localitycode() ended.')
        return True

    def create_opendatamaps(self):
        logger = logging.getLogger(__name__)
        logger.debug('create_localitycode() start.')
        # カーソルを取得
        with self.conn.cursor() as cur:
            # opendatamapsテーブルを作成する
            sql = '''CREATE TABLE opendatamaps (
                      locality_code CHAR(6) NOT NULL,
                      kind     VARCHAR(60) NOT NULL,
                      dataset  VARCHAR(90) NOT NULL,
                      id       VARCHAR(16) NOT NULL,
                      label    VARCHAR(128) NOT NULL,
                      lat      FLOAT NOT NULL,
                      lng      FLOAT NOT NULL,
                      info     TEXT,
                      CONSTRAINT opendatamaps_pkey PRIMARY KEY (locality_code, dataset, id, label)
                  );
                  '''
            # SQL実行
            cur.execute(sql)
            cur.close()
            logger.debug('TABLE(opendatamaps) created.')
        if True:
            with self.conn.cursor() as cur:
                # インデックスを作成する
                sql = '''CREATE INDEX opendatamaps_index1 ON opendatamaps (
                          kind
                      );
                      '''
                # SQL実行
                cur.execute(sql)
                cur.close()
                logger.debug('INDEX(opendatamaps_index1) created.')
        self.conn.commit()
        logger.debug('commited.')
        logger.debug('create_opendatamaps() ended.')
        return True

    def load_tables(self, tables):
        logger = logging.getLogger(__name__)
        logger.debug('load_tables() start, tables=' + str(tables))
        if 'localitycode' in tables:
            self.load_localitycode()
        if 'opendatamaps' in tables:
            # キャッシュディレクトリ全て（ディレクトリ１階層）
            # ToDo: self.load_opendatamaps()
            # ディレクトリ単位（ディレクトリ２階層）
            self.load_opendatamaps_in_dir(tables)
        logger.debug('load_tables() ended.')
        return True

    def load_localitycode(self):
        logger = logging.getLogger(__name__)
        logger.debug('load_localitycode() start.')
        msg = 'localitycodeテーブルにデータをロードします。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # localitycodeテーブルにCSV形式データをロードする
        crawler_dir = os.path.join(BASE_DIR, 'djangoapp' , 'crawler')
        sql_insert = "INSERT INTO localitycode" \
                + " (code, state_name, locality_name, state_yomi, locality_yomi)" \
                + " VALUES ('{code}','{state_name}','{locality_name}'," \
                + "'{state_yomi}','{locality_yomi}');"
        commit = False
        with open(os.path.join(crawler_dir, self.LOCALITYCODE_CSV), 'r') as hf:
            hcsv = csv.reader(hf)
            with self.conn.cursor() as cur:
                for i, rec in enumerate(hcsv):
                    # logger.debug('rec['+str(i)+']=' + str(rec))
                    if i < 1:
                        continue
                    jdata = {'code': rec[0], 'state_name': rec[1], 'locality_name': rec[2],
                            'state_yomi': rec[3], 'locality_yomi': rec[4]}
                    sql = sql_insert.format(**jdata)
                    logger.debug('sql=' + sql)
                    cur.execute(sql)
                    commit = True
                    if self.COMMIT_COUNT > 0 and (i % self.COMMIT_COUNT) == (self.COMMIT_COUNT - 1):
                        self.conn.commit()
                        logger.debug('committed, count=' + str(i+1))
                        commit = False
        if commit:
            self.conn.commit()
            logger.debug('committed last.')
        msg = 'localitycodeテーブルにデータをロードしました。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        logger.debug('load_localitycode() ended.')
        return True

    def load_opendatamaps(self):
        logger = logging.getLogger(__name__)
        logger.debug('load_opendatamaps() start, root_dir=' + str(root_dir))
        # 実行
        msg = 'opendatamapsテーブルにデータをロードします。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        for dir in sorted(os.listdir(self.cache_dir)):
            if dir[0] == '.':
                continue
            msg = 'dir=' + dir
            logger.debug(msg)
            print(msg, file=sys.stderr)
            load_opendatamaps_dir(os.path.join(self.cache, dir))

        msg = 'opendatamapsテーブルにデータをロードしました。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # 復帰
        logger.debug('load_opendatamaps() ended.')
        return True

    def load_opendatamaps_dir(self, dir):
        logger = logging.getLogger(__name__)
        logger.debug('load_opendatamaps_dir() start, dir=' + str(dir))
        # 実行
        if not os.path.isdir(dir):
            msg = 'dir is not directory, dir=' + str(dir)
            logger.debug(msg)
            print(msg, file=sys.stderr)
            return False
        # opendatamapsテーブルにJSON形式データをロードする
        sql_insert = "INSERT INTO opendatamaps" \
                + " (locality_code, kind, dataset, id, label, lat, lng, info)" \
                + " VALUES ('{locality_code}',{ekind}'{kind}'," \
                + "{edataset}'{dataset}','{id}'," \
                + "{elabel}'{label}',{lat},{lng},{einfo}'{info}');"
        for file in sorted(os.listdir(dir)):
            if file[0] == '.':
                continue
            msg = 'loading file=' + file
            logger.debug(msg)
            print('  '+msg+'：', file=sys.stderr, end='')
            with self.conn.cursor() as cur:
                jfile = os.path.join(dir, file)
                sql = ''
                r_count = 0
                commit = False
                try:
                    with open(jfile, 'r') as fh:
                        jrecs = json.loads(fh.read())
                        # logger.debug('jrecs='+jfile+', content='+str(jrecs))
                        for i, rec in enumerate(jrecs):
                            # logger.debug('rec['+str(i)+']=' + str(rec))
                            jdata = {'locality_code': rec['locality_code'], 'kind': rec['kind'],
                                    'dataset': rec['dataset'],
                                    'id': rec['id'], 'label': rec['label'],
                                    'lat': rec['lat'], 'lng': rec['lng'],
                                    'info': json.dumps(rec['info'], ensure_ascii=False),
                                    'ekind': '', 'edataset': '', 'elabel': '', 'einfo': ''}
                            for key in ['kind', 'dataset', 'label', 'info']:
                                ev = jdata[key].replace('\\','\\\\').replace("'","\\'")
                                if ev != jdata[key]:
                                    jdata['e'+key] = 'E'
                                    jdata[key] = ev
                            if jdata['lat'] == '':
                                jdata['lat'] = 0.0
                            if jdata['lng'] == '':
                                jdata['lng'] = 0.0
                            sql = sql_insert.format(**jdata)
                            # logger.debug('sql=' + sql)
                            cur.execute(sql)
                            r_count += 1
                            commit = True
                            if self.COMMIT_COUNT > 0 and (i % self.COMMIT_COUNT) == (self.COMMIT_COUNT - 1):
                                self.conn.commit()
                                logger.debug('committed, count=' + str(i+1))
                                commit = False
                    if commit:
                        self.conn.commit()
                        logger.debug('committed last.')
                    msg = str(r_count) + '件'
                    print(msg, file=sys.stderr)
                    logger.debug(msg)
                except psycopg2.errors.UniqueViolation as e:
                    logger.exception(e)
                    logger.error('loading about, sql=' + sql)
                    self.conn.rollback()
                    print('ユニークキー例外が発生', file=sys.stderr)
                except psycopg2.OperationalError as e:
                    logger.exception(e)
                    logger.error('loading about, e.args=' + str(e.args))
                    if len(e.args) > 0 and e.args[0] == 'SSL connection has been closed unexpectedly\n':
                        self.conn = None
                        time.sleep(5)
                        self.connect()
                        cur = self.conn.cursor()
                        logger.warning('DBのコネクションを再接続済')
                        print('DBへのコネクションが切断され、再接続済', file=sys.stderr)
                    else:
                        raise Exception('SQLの実行失敗')
        # 復帰
        logger.debug('load_opendatamaps_dir() ended.')
        return True

    def load_opendatamaps_in_dir(self, dirs):
        logger = logging.getLogger(__name__)
        logger.debug('load_opendatamaps_in_dir() start.')
        # 実行
        msg = 'opendatamapsテーブルにデータをロードします。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # ディレクトリを辿る
        dir_list = []
        for dir in dirs:
            if dir == 'localitycode' or dir == 'opendatamaps':
                continue
            dir_list.append(dir.split('/'))
        for dir1 in sorted(os.listdir(self.cache_dir)):
            if dir1[0] == '.':
                continue
            logger.debug('dir1=' + dir1)
            dir1_list = dir1.split('_')
            if len(dir1_list) != 2:
                continue
            dir1_exec = False
            if dir_list == []:
                dir1_exec = True
            else:
                for dir in dir_list:
                    if dir1_list[1] == dir[0]:
                        dir1_exec = True
                        break
            if not dir1_exec:
                continue
            dir1_path = os.path.join(self.cache_dir, dir1)
            if not os.path.isdir(dir1_path):
                continue
            for dir2 in sorted(os.listdir(os.path.join(dir1_path))):
                if dir2[0] == '.':
                    continue
                logger.debug('dir2=' + dir2)
                dir2_list = dir2.split('_')
                if len(dir2_list) != 2:
                    continue
                dir2_exec = False
                if dir_list == []:
                    dir2_exec = True
                else:
                    for dir in dir_list:
                        if dir[0] == dir1_list[1]:
                            if len(dir) == 1:
                                dir2_exec = True
                                break
                            elif dir[1] == dir2_list[1]:
                                dir2_exec = True
                                break
                if not dir2_exec:
                    continue
                dir2_path = os.path.join(dir1_path, dir2)
                if not os.path.isdir(dir2_path):
                    continue
                # ロード範囲のデータを削除する
                # ToDo: self.delete_opendatamaps_dir(dir2_path)
                print('dir=' + dir1 + '/' + dir2, file=sys.stderr)
                self.load_opendatamaps_dir(dir2_path)

        msg = 'opendatamapsテーブルにデータをロードしました。'
        logger.info(msg)
        print(msg, file=sys.stderr)
        logger.debug('load_opendatamaps_in_dir() ended.')
        return True

    def drop_tables(self, tables):
        logger = logging.getLogger(__name__)
        logger.debug('drop_tables() start.')
        # 指定されたテーブルを削除する
        droped = False
        for table in ['opendatamaps', 'localitycode']:
            if table in tables:
                with self.conn.cursor() as cur:
                    # opendatamapsテーブルの存在確認
                    sql = "SELECT COUNT(*) FROM information_schema.tables" \
                            + " WHERE table_name = '" + table + "';"
                    # SQL実行
                    cur.execute(sql)
                    rows = cur.fetchall()
                    logger.debug(table + ' COUNT()=' + str(rows[0][0]))
                    if int(rows[0][0]) > 0:
                        # テーブルを削除する
                        sql = "DROP TABLE " + table + ";"
                        # SQL実行
                        cur.execute(sql)
                        droped = True
                    cur.close()
                    logger.debug('TABLE(' + table + ') droped.')
        if droped:
            self.conn.commit()
        logger.debug('drop_tables() ended.')
        return True

    def get_opendatamaps_kinds(self, codes):
        """
        opendatamapsテーブルの種別(kind)一覧を取得する。
        :param codes: list型、市区町村コードのリストを指定する。省略する場合はNoneまたは[]を指定する。
        :return: list型、str型種別(kind)のリストを返却する。
        """
        logger = logging.getLogger(__name__)
        logger.debug('get_opendatamaps_kinds() start.')
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
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
        rc = {'kinds': [rec[0] for rec in recs]}
        logger.debug('get_opendatamaps_kinds() ended, rc=' + str(rc))
        return rc

    def get_summary(self):
        """
        opendatamapsとlocalitycodeテーブルからデータ一覧(code,state_name,locality_name,kind,count(*))を取得する。
        :return: list型、レコード(code,state_name,locality_name,kind,count(*))のリストを返却する。
        """
        logger = logging.getLogger(__name__)
        logger.debug('get_summary() start.')
        rc = None
        sel_dict = {'codes': ''}
        # 検索実行
        sql = '''SELECT f.locality_code,f.kind,MAX(c.state_name),MAX(c.locality_name),COUNT(*)
                 FROM opendatamaps f JOIN localitycode c ON f.locality_code = c.code
                 GROUP BY f.locality_code,f.kind ORDER BY f.locality_code,f.kind;'''
        with self.conn.cursor() as cur:
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
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
        # logger.debug('rc=' + str(rc))
        logger.debug('get_summary() ended, len(rc)=' + str(len(rc)))
        return rc

    def get_by_localitycode(self, codes, kinds, limit=QUERY_LIMIT):
        """
        指定した都道府県コードまたｈ市区町村コードおよびデータ種別を含むレコードリストを検索して返却する。
        :param codes: list型、都道府県コードまたｈ市区町村コードを指定する。省略する場合はNoneを指定する。例：['22203','22206']
        :param kinds: list型、データ種別をリストで指定する。省略する場合はNoneを指定する。例：['公衆トイレ']
        :param limit: int型、最大返却数、省略値=100件、0またはNoneを指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリスト
        """
        logger = logging.getLogger(__name__)
        logger.debug('get_by_localitycode() start.')
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
            not_in_kinds = [k[1:] for k in kinds if [k[0] == '!' and len(k) > 1]
            if len(in_kinds) > 0:
                sel_dict['kinds'] = "AND kind IN " + "('" + "','".join(in_kinds) + "')"
            if len(not_in_kinds) > 0:
                sel_dict['kinds'] = "AND kind NOT IN " + "('" + "','".join(not_in_kinds) + "')"
        if sel_dict['codes'] != '' and sel_dict['kinds'] != '':
            sel_dict['AND'] = ' AND '
        if limit is not None and limit > 0:
            sel_dict['limit'] = " LIMIT " + str(limit)
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
        rc = [{'locality_code': rec[0],
               'kind': rec[1],
               'id': rec[2],
               'label': rec[3],
               'lat': rec[4],
               'lng': rec[5],
               'info': rec[6],
              } for rec in recs]
        logger.debug('get_by_localitycode() ended, len(rc)=' + str(len(rc)))
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
        logger = logging.getLogger(__name__)
        logger.debug('get_by_distance_from_center() start.')
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
            in_kinds = [k for k in kinds if k[0] != '!']
            not_in_kinds = [k[1:] for k in kinds if [k[0] == '!' and len(k) > 1]
            if len(in_kinds) > 0:
                sel_dict['kinds'] = "AND kind IN " + "('" + "','".join(in_kinds) + "')"
            if len(not_in_kinds) > 0:
                sel_dict['kinds'] = "AND kind NOT IN " + "('" + "','".join(not_in_kinds) + "')"
        if limit is None:
            limit = QUERY_LIMIT
        with self.conn.cursor() as cur:
            sql = sel_sql.format(**sel_dict)
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
        rc = [{'locality_code': rec[0],
               'kind': rec[1],
               'id': rec[2],
               'label': rec[3],
               'lat': rec[4],
               'lng': rec[5],
               'info': rec[6],
               'distance': self.calc_distance((c_lat,c_lng), (rec[4],rec[5]))
              } for rec in recs]
        # logger.debug('rc=' + str(rc))
        # 中心からの距離の近い順にソートする
        rc = [rec for rec in rc if rec['distance'] <= distance]
        rc.sort(key=lambda x: x['distance'])
        if limit > 0 and len(rc) > limit:
            rc = rc[:limit]
        # logger.debug('sorted rc=' + str(rc))
        logger.debug('get_by_distance_from_center() ended, len(rc)=' + str(len(rc)))
        return rc

    def calc_distance(self, center, target):
        """
        中心から対象までの直線距離を求める。
        :param center: list型、中心の緯度・経度を(lat, lng)で指定する。緯度・経度はfloat型。
        :param target: list型、対象の緯度・経度を(lat, lng)で指定する。緯度・経度はfloat型。
        :return: int型、対象までの直線距離。単位はメートル(m)。
        """
        if target[0] is None or target[0] == 0.0 \
        or target[1] is None or target[1] == 0.0:
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
        logger = logging.getLogger(__name__)
        logger.debug('get_localitycode_by_code() start, code=' + str(code))
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
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
        rc = [{'code': rec[0],
               'state_name': rec[1],
               'locality_name': rec[2]
              } for rec in recs]
        logger.debug('get_localitycode_by_code() ended, rc=' + str(len(rc)))
        return rc

    def get_localitycode_by_name(self, state, locality, limit=QUERY_LIMIT):
        """
        localitycodeテーブルをstate_nameおよびlocality_nameで検索して結果を返却する。
        :param state: str型、都道府県名、省略した場合は検索条件としない。
        :param locality: str型、市区町村名、省略した場合は検索条件としない。
        :param limit: int型、最大返却数、省略またはNone指定時は100件。0を指定した場合は無制限。
        :return: list型、JSON型検索結果レコードのリストを返却する。
        """
        logger = logging.getLogger(__name__)
        logger.debug('get_localitycode_by_name() start, state=' + str(state) + ', locality=' + str(locality))
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
            logger.debug('sql=' + sql)
            # SQL実行
            cur.execute(sql)
            recs = cur.fetchall()
            logger.debug('select len(recs)=' + str(len(recs)))
            # logger.debug('select recs=' + str(recs))
            cur.close()
        # JSON形式に嫌韓する
        rc = [{'code': rec[0],
               'state_name': rec[1],
               'locality_name': rec[2]
              } for rec in recs]
        logger.debug('get_localitycode_by_code() ended, rc=' + str(len(rc)))
        return rc

def setup_logger(name, level, log_file='opendatadb.log', log_dir='log'):
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
    BASE_DIR=os.path.join(os.environ['HOME'], 'github', 'opendatamaps')
    db = None
    try:
        # パラメタチェック
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument('-c', '--create', action='store_true', help='テーブルを定義する。')
        p.add_argument('-d', '--drop', action='store_true', help='テーブルを削除する。')
        p.add_argument('-l', '--load', action='store_true', help='テーブルにデータをロードする。')
        p.add_argument('-t', '--test', action='store_true', help='テーブルを検索する。')
        p.add_argument('tables', nargs='*', default=[], help='処理対象テーブル名（localitycode、opendatamaps）を指定する。複数指定可能。')
        args = p.parse_args(sys.argv[1:])
        # 開始
        msg = 'opendatadb.py start.'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # DB接続
        db = opendatadb()
        db.connect()
        # 処理開始
        if args.drop:
            db.drop_tables(args.tables)
            msg = 'テーブルを削除しました。'
            logger.info(msg)
            print(msg, file=sys.stderr)
        if args.create:
            db.create_tables(args.tables)
            msg = 'テーブルを定義しました。'
            logger.info(msg)
            print(msg, file=sys.stderr)
        if args.load:
            # データロード
            db.load_tables(args.tables)
        if args.test:
            if args.tables == [] or 'localitycode' in args.tables:
                # localitycodeテーブルテスト
                recs = db.get_localitycode_by_code('22206%')
                print('get_localitycode_by_code(22206%) recs=' + str(recs))
                recs = db.get_localitycode_by_code('22206')
                print('get_localitycode_by_code(22206) recs=' + str(recs))
                recs = db.get_localitycode_by_code(None, limit=2)
                print('get_localitycode_by_code(None,limit=2) recs=' + str(recs))
                recs = db.get_localitycode_by_name('静岡県', '三島市')
                print('get_localitycode_by_name(静岡県,三島市) recs=' + str(recs))
                recs = db.get_localitycode_by_name('静岡県', None, limit=3)
                print('get_localitycode_by_name(静岡県,None,limit=3) recs=' + str(recs))
                recs = db.get_localitycode_by_name(None, '三島市')
                print('get_localitycode_by_name(None,三島市) recs=' + str(recs))
                recs = db.get_localitycode_by_name(None, None, limit=2)
                print('get_localitycode_by_name(None,None,limit=2) recs=' + str(recs))
            if args.tables == [] or 'opendatamaps' in args.tables:
                # opendatamapsテーブルテスト
                res = db.get_opendatamaps_kinds(None)
                print('opendatamaps_kinds() res=' + str(res))
                res = db.get_opendatamaps_kinds(['22206'])
                print('opendatamaps_kinds([22206]) res=' + str(res))
                recs = db.get_by_localitycode(['22206'], ['眺望地点'])
                print('opendatamaps([22206],[眺望地点]) recs=' + str(recs))
                recs = db.get_by_localitycode(['22203','22206'], None, limit=3)
                print('opendatamaps([22203,22206],None,limit=2) recs=' + str(recs))
                recs = db.get_by_localitycode(None, ['公衆トイレ'], limit=1)
                print('opendatamaps(None,[公衆トイレ],limit=3) recs=' + str(recs))
                latlng = (35.118590536070734, 138.91855992264092)   # 三島市役所
                recs = db.get_by_distance_from_center(latlng[0], latlng[1], 500, ['公衆トイレ','薬局'])
                print('opendatamaps(三島市役所±500m,[公衆トイレ,薬局]) recs=' + str(recs))
                recs = db.get_by_distance_from_center(latlng[0], latlng[1], 500, ['公衆トイレ','薬局'], limit=1)
                print('opendatamaps(三島市役所±500m,[公衆トイレ,薬局],limit=1) recs=' + str(recs))
                recs = db.get_by_distance_from_center(latlng[0], latlng[1], 500, None, limit=2)
                print('opendatamaps(三島市役所±500m,None,limit=2) recs=' + str(recs))

    except Exception as e:
        logger.exception(e)
        print(e, file=sys.stderr)
        rc = 99

    # 終了処理
    if db is not None:
        db.disconnect()
    db = None

    # 復帰
    msg = 'opendatadb.py ended, rc=' + str(rc)
    logger.info(msg)
    print(msg, file=sys.stderr)
    sys.exit(rc)
