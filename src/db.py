#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# db.py: オープンデータDBの処理クラス
# Copyright (C) N.Togashi 2025-2026
# Required environmental variables:
#   POSTGRESQL_HOST
#   POSTGRESQL_PORT
#   POSTGRESQL_USER
#   POSTGRESQL_PASS
#   POSTGRESQL_DBNAME
# How to check results: 
#   $ psql -h $POSTGRESQL_HOST -U $POSTGRESQL_USER -p $POSTGRESQL_PORT
#   Password for user postgres: <value of $POSTGRESQL_PASS>
#   postgres=# \d opendatamaps
#   postgres=# SELECT COUNT(*) FROM opendatamaps;
#   postgres=# SELECT COUNT(*) FROM localitycode;
#   postgres=# \q

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

class OpendataMapsDb:

    COMMIT_COUNT = 100
    LOCALITYCODE_CSV = '都道府県コード及び市区町村コード_20240101.csv'
    conn = None
    cache_dir = None
    download_dir = None
    logger = None

    def __init__(self, logname=''):
        if logname == '':
            my_logname = __name__
        else:
            my_logname = logname + '.db'
        self.logger = logging.getLogger(my_logname)
        self.logger.debug('__init__() start.')
        if 'BASE_DIR' not in locals():
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = os.path.join(BASE_DIR, 'cache')
        self.download_dir = os.path.join(BASE_DIR, 'download')
        self.logger.debug('__init__() ended.')

    def connect(self):
        self.logger.debug('connect() start.')
        # PostgreSQLサーバへ接続
        if self.conn is None:
            self.conn = psycopg2.connect('host=' + os.getenv('POSTGRESQL_HOST') \
                    +' port=' + os.getenv('POSTGRESQL_PORT') \
                    +' dbname=' + os.getenv('POSTGRESQL_DBNAME') \
                    +' user=' + os.getenv('POSTGRESQL_USER') \
                    +' password=' + os.getenv('POSTGRESQL_PASS'))
            self.logger.debug('connected.')
        self.logger.debug('connect() ended.')
        return self.conn

    def disconnect(self):
        self.logger.debug('disconnect() start.')
        # 接続を閉じる
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.logger.debug('disconnected.')
        self.logger.debug('disconnect() ended.')
        return True

    def create_tables(self, tables):
        self.logger.debug('create_tables() start, tables=' + str(tables))
        if 'localitycode' in tables:
            self.create_localitycode();
        if 'opendatamaps' in tables:
            self.create_opendatamaps();
        self.logger.debug('create_tables() ended.')
        return True

    def create_localitycode(self):
        self.logger.debug('create_localitycode() start.')
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
            self.logger.debug('TABLE(localitycode) created.')

        if True:
            # インデックスを作成する
            with self.conn.cursor() as cur:
                sql = '''CREATE INDEX localitycode_index1 ON localitycode (
                          state_name
                      );
                      '''
                # SQL実行
                cur.execute(sql)
                cur.close()
                self.logger.debug('INDEX(localitycode_index1) created.')

            with self.conn.cursor() as cur:
                sql = '''CREATE INDEX localitycode_index2 ON localitycode (
                          locality_name
                      );
                      '''
                # SQL実行
                cur.execute(sql)
                cur.close()
                self.logger.debug('INDEX(localitycode_index2) created.')

        self.conn.commit()
        self.logger.debug('commited.')
        self.logger.debug('create_localitycode() ended.')
        return True

    def create_opendatamaps(self):
        self.logger.debug('create_localitycode() start.')
        # カーソルを取得
        with self.conn.cursor() as cur:
            # opendatamapsテーブルを作成する
            sql = '''CREATE TABLE opendatamaps (
                      locality_code CHAR(6) NOT NULL,
                      kind     VARCHAR(64) NOT NULL,
                      dataset  VARCHAR(128) NOT NULL,
                      id       VARCHAR(64) NOT NULL,
                      label    VARCHAR(512) NOT NULL,
                      lat      FLOAT NOT NULL,
                      lng      FLOAT NOT NULL,
                      info     TEXT,
                      error    TEXT,
                      CONSTRAINT opendatamaps_pkey PRIMARY KEY (locality_code, dataset, id, label)
                  );
                  '''
            # SQL実行
            cur.execute(sql)
            cur.close()
            self.logger.debug('TABLE(opendatamaps) created.')

        if True:
            # インデックスを作成する
            with self.conn.cursor() as cur:
                sql = '''CREATE INDEX opendatamaps_index1 ON opendatamaps (
                          lat, lng, kind
                      );
                      '''
                # SQL実行
                cur.execute(sql)
                cur.close()
                self.logger.debug('INDEX(opendatamaps_index1) created.')

            with self.conn.cursor() as cur:
                sql = '''CREATE INDEX opendatamaps_index2 ON opendatamaps (
                          locality_code, kind
                      );
                      '''
                # SQL実行
                cur.execute(sql) 
                cur.close()
                self.logger.debug('INDEX(opendatamaps_index2) created.')

        self.conn.commit()
        self.logger.debug('commited.')
        self.logger.debug('create_opendatamaps() ended.')
        return True

    def load_tables(self, tables, files):
        self.logger.debug('load_tables() start, tables=' + str(tables) \
                + ', files=' + str(files))
        if 'localitycode' in tables:
            self.load_localitycode()
        if 'opendatamaps' in tables:
            if files is None or files == []:
                files = [os.path.join(self.cache_dir, f) \
                        for f in sorted(os.listdir(self.cache_dir)) \
                        if f[0] != '.']
            # 再帰的にロードする
            msg = 'opendatamapsテーブルにデータをロードします。' 
            self.logger.info(msg)
            print(msg, file=sys.stderr)
            self.load_opendatamaps(files)
            msg = 'opendatamapsテーブルにデータをロードしました。' 
            self.logger.info(msg)
            print(msg, file=sys.stderr)
        self.logger.debug('load_tables() ended.')
        return True

    def load_localitycode(self):
        self.logger.debug('load_localitycode() start.')
        msg = 'localitycodeテーブルにデータをロードします。'
        self.logger.info(msg)
        print(msg, file=sys.stderr)
        # localitycodeテーブルにCSV形式データをロードする
        sql_insert = "INSERT INTO localitycode" \
                + " (code, state_name, locality_name, state_yomi, locality_yomi)" \
                + " VALUES ('{code}','{state_name}','{locality_name}'," \
                + "'{state_yomi}','{locality_yomi}');"
        commit = False
        with open(os.path.join(self.download_dir, self.LOCALITYCODE_CSV), 'r') as hf:
            hcsv = csv.reader(hf)
            with self.conn.cursor() as cur:
                uniq_code = {}
                for i, rec in enumerate(hcsv):
                    # self.logger.debug('rec['+str(i)+']=' + str(rec))
                    if i < 1:
                        continue
                    if rec[0] in uniq_code:
                        self.logger.warning('市区町村コードが重複, rec['+str(i)+']=' + str(rec))
                        uniq_code[rec[0]] += 1
                        continue
                    uniq_code[rec[0]] = 1
                    jdata = {'code': rec[0], 'state_name': rec[1], 'locality_name': rec[2],
                            'state_yomi': rec[3], 'locality_yomi': rec[4]}
                    sql = sql_insert.format(**jdata)
                    # self.logger.debug('sql=' + sql)
                    cur.execute(sql)
                    commit = True
                    if self.COMMIT_COUNT > 0 and (i % self.COMMIT_COUNT) == (self.COMMIT_COUNT - 1):
                        self.conn.commit()
                        self.logger.debug('committed, count=' + str(i+1))
                        commit = False
        if commit:
            self.conn.commit()
            self.logger.debug('committed last.')
        msg = 'localitycodeテーブルにデータをロードしました。'
        self.logger.info(msg)
        print(msg, file=sys.stderr)
        self.logger.debug('load_localitycode() ended.')
        return True

    def load_opendatamaps(self, files):
        self.logger.debug('load_opendatamaps() start, files=' + str(files))
        # 実行
        for file in files:
            if file[0] == '.':
                continue
            if os.path.isdir(file):
                # ディレクトリを処理する
                msg = 'dir=' + str(file)
                self.logger.debug(msg)
                print(msg, file=sys.stderr)
                files_in_dir = [os.path.join(file, f) \
                        for f in sorted(os.listdir(file), reverse=True) \
                        if f[0] != '.']
                # 下階層を処理する
                self.load_opendatamaps(files_in_dir)
            else:
                # ファイルを処理する
                msg = 'loading file=' + file
                self.logger.debug(msg)
                print('  '+msg+'：', file=sys.stderr, end='')
                uniq_key_error = False
                try:
                    with self.conn.cursor() as cur:
                        rc = self.insert_opendatamaps_file(cur, file)
                except psycopg2.errors.UniqueViolation as e:
                    uniq_key_error = True

                # ユニークキーエラーが発生していれば１件づつ登録する
                if uniq_key_error:
                    with self.conn.cursor() as cur:
                        rc = self.insert_opendatamaps_file(cur, file, commit1=True)

        # 復帰
        self.logger.debug('load_opendatamaps() ended.')
        return True

    def insert_opendatamaps_file(self, cur, file, commit1=False):
        """
        """
        self.logger.debug('insert_record() start.')
        # 実行
        sql_insert = "INSERT INTO opendatamaps" \
                + " (locality_code, kind, dataset, id, label, lat, lng, info, error)" \
                + " VALUES ('{locality_code}',{ekind}'{kind}'," \
                + "{edataset}'{dataset}','{id}'," \
                + "{elabel}'{label}',{lat},{lng},{einfo}{info},{eerror}{error});"
        sql = ''
        r_count = 0
        commit = False
        with open(file, 'r') as hf:
            jrecs = json.loads(hf.read())
            # self.logger.debug('jrecs='+file+', content='+str(jrecs))
            for i, rec in enumerate(jrecs):
                # self.logger.debug('rec['+str(i)+']=' + str(rec))
                jdata = {'locality_code': rec['locality_code'], 'kind': rec['kind'],
                        'dataset': rec['dataset'],
                        'id': rec['id'], 'label': rec['label'],
                        'lat': rec['lat'], 'lng': rec['lng'],
                        'info': 'NULL', 'error': 'NULL',
                        'ekind': '', 'edataset': '', 'elabel': '',
                        'einfo': '', 'eerror': ''}
                if 'info' in rec and rec['info'] != '':
                    jdata['info'] = json.dumps(rec['info'], ensure_ascii=False)
                if 'error' in rec and rec['error'] != '':
                    jdata['error'] = rec['error']
                for key in ['kind', 'dataset', 'label', 'info', 'error']:
                    ev = jdata[key].replace('\\','\\\\').replace("'","\\'")
                    if ev != jdata[key]:
                        jdata['e'+key] = 'E'
                        jdata[key] = ev
                if jdata['info'] != 'NULL':
                    jdata['info'] = "'" + jdata['info'] + "'"
                if jdata['error'] != 'NULL':
                    jdata['error'] = "'" + jdata['error'] + "'"
                if jdata['lat'] == '':
                    jdata['lat'] = 0.0
                if jdata['lng'] == '':
                    jdata['lng'] = 0.0
                sql = sql_insert.format(**jdata)
                # self.logger.debug('sql=' + sql)
                complete = False
                while not complete:
                    try:
                        cur.execute(sql)
                        commit = True
                        if commit1 \
                        or self.COMMIT_COUNT > 0 and (i % self.COMMIT_COUNT) == (self.COMMIT_COUNT - 1):
                            self.conn.commit()
                            commit = False
                            if not commit1:
                                self.logger.debug('committed, count=' + str(i+1))
                        r_count += 1
                        complete = True
                    except psycopg2.errors.UniqueViolation as e:
                        self.logger.exception(e)
                        self.conn.rollback()
                        msg = 'ユニークキー例外が発生1'
                        self.logger.error(msg)
                        if not commit1:
                            print(msg, file=sys.stderr)
                            raise e
                        complete = True
                    except psycopg2.OperationalError as e:
                        self.logger.exception(e)
                        self.logger.debug('loading about, e.args=' + str(e.args))
                        if len(e.args) > 0 and e.args[0] == 'SSL connection has been closed unexpectedly\n':
                            self.conn = None
                            time.sleep(5)
                            self.connect()
                            cur = self.conn.cursor()
                            msg = 'DBへのコネクションが切断され、再接続済1'
                            self.logger.warning(msg)
                            print(msg, file=sys.stderr)
                            if not commit1:
                                raise e
                        else:
                            msg = 'SQLの実行失敗1'
                            self.logger.warning(msg)
                            print(msg, file=sys.stderr)
                            raise Exception(msg)
                    except Exception as e:
                        self.logger.exception(e)
                        msg = 'SQLの実行失敗2'
                        self.logger.warning(msg)
                        print(msg, file=sys.stderr)
                        raise Exception(msg)
        if commit:
            try:
                self.conn.commit()
            except psycopg2.errors.UniqueViolation as e:
                self.logger.exception(e)
                self.conn.rollback()
                msg = 'ユニークキー例外が発生2'
                self.logger.error(msg)
                print(msg, file=sys.stderr)
                raise e
            except psycopg2.OperationalError as e:
                self.logger.exception(e)
                self.logger.debug('loading about, e.args=' + str(e.args))
                if len(e.args) > 0 and e.args[0] == 'SSL connection has been closed unexpectedly\n':
                    self.conn = None
                    time.sleep(5)
                    self.connect()
                    # cur = self.conn.cursor()
                    msg = 'DBへのコネクションが切断され、再接続済2'
                    self.logger.warning(msg)
                    print(msg + '：', file=sys.stderr, end='')
                else:
                    msg = 'SQLの実行失敗3'
                    print(msg, file=sys.stderr)
                raise Exception(msg)
            except Exception as e:
                self.logger.exception(e)
                msg = 'SQLの実行失敗4'
                print(msg, file=sys.stderr)
                raise Exception(msg)
            self.logger.debug('committed last.')

        msg = str(r_count) + '件'
        print(msg, file=sys.stderr)
        self.logger.debug(msg)
        # 復帰
        self.logger.debug('insert_record() ended, rc=' + str(rc))
        return True

    def drop_tables(self, tables):
        self.logger.debug('drop_tables() start.')
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
                    self.logger.debug(table + ' COUNT()=' + str(rows[0][0]))
                    if int(rows[0][0]) > 0:
                        # テーブルを削除する
                        sql = "DROP TABLE " + table + ";"
                        # SQL実行
                        cur.execute(sql)
                        droped = True
                    cur.close()
                    self.logger.debug('TABLE(' + table + ') droped.')
        if droped:
            self.conn.commit()
        self.logger.debug('drop_tables() ended.')
        return True

    def delete_records(self, keys):
        """
        opendatamapsテーブルのレコードを削除する。
        :param keys: list型、都道府県名[/市区町村名]
        :return: boolean型、True=正常終了、False=異常終了
        """
        self.logger.debug('delete_records() start, key=' + str(keys))
        # 削除実行
        rc = True
        deleted = False
        for key in keys:
            self.logger.debug('key=' + str(key))
            key_parse = key.split('/')
            if len(key_parse) > 2:
                msg = '削除するレコードの指定に誤りがあります。' + key
                self.logger.error(msg)
                raise Exception(msg)
            # 都道府県・市区町村コードを取得する
            sql = "SELECT * FROM localitycode WHERE state_name='" \
                + key_parse[0] + "' AND locality_name='"
            if len(key_parse) > 1:
                sql += key_parse[1]
            sql += "';"
            # SQL実行
            with self.conn.cursor() as cur:
                self.logger.debug('sql=' + sql)
                cur.execute(sql)
                rows = cur.fetchall()
                cur.close()
                self.logger.debug('rows=' + str(rows))
                if len(rows) != 1:
                    msg = '削除対象の都道府県名または市区町村名に誤りがあります。' + key
                    self.logger.error(msg)
                    raise Exception(msg)
            lcd = rows[0][0]
            with self.conn.cursor() as cur:
                sql = "DELETE FROM opendatamaps WHERE "
                if len(key_parse) == 1:
                    sql += "SUBSTR(locality_code,1,2)='" + lcd[0:2] + "'"
                else:
                    sql += "locality_code='" + lcd + "'"
                # SQL実行
                row_count = 0
                self.logger.debug('sql=' + sql)
                cur.execute(sql)
                row_count = cur.rowcount
                deleted = True
                cur.close()

            if deleted:
                self.conn.commit()
                deleted = False

            print('  ' + key + ': ' + str(row_count) + 'レコードが削除されました。')

        if deleted:
            self.conn.commit()
        self.logger.debug('delete_records() ended, rc=' + str(rc))
        return rc

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

def setup_logger(name, level, log_file='db.log', log_dir='log'):
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
    db = None
    try:
        # パラメタチェック
        import argparse
        p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, \
            description='    テーブル名にはlocalitycode、opendatamapsが指定できる。')
        p.add_argument('-c', '--create', type=str, nargs='*', default=None, \
                help='テーブルを定義する。\n' \
                     'CREATE: 定義するテーブル名を指定する。複数指定可能、省略可能。')
        p.add_argument('-d', '--drop', type=str, nargs='*', default=None, \
                help='テーブルを削除する。\n' \
                     'DROP: 削除するテーブル名を指定する。複数指定可能、省略可能。')
        p.add_argument('-e', '--delete', type=str, nargs='*', default=None, \
                help='opendatamapsテーブルのレコードを削除する。\n' \
                     'DELETE: 削除対象を「都道府県名[/市区町村名]」で指定する。')
        p.add_argument('-l', '--load', type=str, nargs='+', default=None, \
                help='テーブルにデータをロードする。\n' \
                     'LOAD: データをロードするテーブル名を指定する。')
        p.add_argument('-f', '--files', type=str, nargs='*', \
                help='opendatamapsテーブルにデータをロードする場合、\n' \
                     'FILES: ロードするディレクトリまたはファイルのパスを指定する。\n' \
                     '省略時はキャッシュディレクトリ内の全ファイルが対象。')
        p.add_argument('-t', '--test', type=str, nargs='*', default=None, \
                help='テーブルを検索する。\n' \
                     'TEST: 検索するテーブル名を指定する。複数指定可能、省略可能。')
        args = p.parse_args(sys.argv[1:])
        # 開始
        msg = 'db.py start.'
        logger.info(msg)
        print(msg, file=sys.stderr)
        # DB接続
        db = OpendataMapsDb()
        db.connect()
        # 処理開始
        if type(args.drop) is list:
            db.drop_tables(args.drop)
            msg = 'テーブルを削除しました。'
            logger.info(msg)
            print(msg, file=sys.stderr)
        if type(args.create) is list:
            db.create_tables(args.create)
            msg = 'テーブルを定義しました。' + str(args.create)
            logger.info(msg)
            print(msg, file=sys.stderr)
        if type(args.load) is list:
            # データロード
            db.load_tables(args.load, args.files)
        if type(args.delete) is list:
            # opendatamapsテーブルのレコード削除
            db.delete_records(args.delete)
        if type(args.test) is list:
            if args.test == [] or 'localitycode' in args.test:
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
            if args.test == [] or 'opendatamaps' in args.test:
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
                recs = db.get_summary()
                print('summary()=')
                for rec in recs:
                    print(str(rec))

    except Exception as e:
        logger.exception(e)
        print(e, file=sys.stderr)
        rc = 99

    # 終了処理
    if db is not None:
        db.disconnect()
    db = None

    # 復帰
    msg = 'db.py ended, rc=' + str(rc)
    logger.info(msg)
    print(msg, file=sys.stderr)
    sys.exit(rc)
