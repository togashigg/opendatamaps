#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# crawler_stdout_summary.py: crawler.pyの結果をサマライズして標準出力に出力する。
# Usage: python3 crawler_stdout_summary.py [crawler.pyの出力ファイル]
#        crawler.pyの標準出力が省略された場合は標準入力から読み込む。
# Copyright (C) N.Togashi 2026

import os
import sys
import datetime
import time
import re
import csv
import json
import copy

# 定数を宣言する
re_state = re.compile(r'^([0-9]{1,2}/[0-9]{1,2}) 【([^】]+)】サイト=([0-9]{6}) [^：]+：http')
re_package = re.compile(r'^([0-9]+)/([0-9]+)\[([^\]]+)\]([^：]+)：(.*)$')
re_make_map = re.compile(r'^([^\:]+)\:\[([^\]]+)\] マップデータを作成しました。$')

def summarize(h_in):
    """
    入力をサマライズする。
    """
    # 初期化
    summary = {}

    # 入力ファイルをチェックする
    first_line = h_in.readline()
    if re.search(r'crawler.py start.', first_line) is None:
        print('ERROR:crawler.pyの標準出力ではないようです！', file=sys.stderr)
        exit(1)

    # サマライズ開始
    state = None
    package = None
    p_no = None
    p_max = None
    for line in h_in:
        line = line.rstrip()
        # print('DEBUG:line=' + line, file=sys.stderr)
        m_state = re_state.match(line)
        if m_state is not None:
            # 都道府県の行
            # print('DEBUG:都道府県の行: ' + line, file=sys.stderr)
            if state is not None:
                if package is not None and package['r_count'] > 0:
                    summary[state]['packages'].append(copy.deepcopy(package))
                    summary[state]['r_sum'] += package['r_count']
                    package = None
                summary[state]['p_no'] = p_no
                summary[state]['p_max'] = p_max
                state = None

            state = m_state.group(3) + '_' + m_state.group(2)
            summary[state] = copy.deepcopy({ \
                               'code':  m_state.group(3), \
                               'name':  m_state.group(2), \
                               'no':    m_state.group(1), \
                               'p_no':  None, \
                               'p_max': None, \
                               'packages': [], \
                               'r_sum': 0 \
                             })
            package = None
            continue

        m_package = re_package.match(line)
        if m_package is not None:
            # パッケージの処理結果
            # print('DEBUG:パッケージの行: ' + line, file=sys.stderr)
            if package is not None and package['r_count'] > 0:
                summary[state]['packages'].append(copy.deepcopy(package))
                summary[state]['r_sum'] += package['r_count']
                package = None
            package = copy.deepcopy({ 'pid':  m_package.group(3), \
                        'name': m_package.group(4), \
                        'kind': None, \
                        'type': [], \
                        'r_count': 0 \
                      })
            p_no = m_package.group(1)
            p_max = m_package.group(2)
            m_make_map = re_make_map.match(m_package.group(5))
            if m_make_map is None:
                continue

            package['kind'] = m_make_map.group(2)
            package['type'].append(m_make_map.group(1))
            package['r_count'] += 1
            continue

        m_make_map = re_make_map.match(line)
        if m_make_map is not None:
            # 2つ目以降のリソースの作成
            # print('DEBUG:リソースの行: ' + line, file=sys.stderr)
            package['type'].append(m_make_map.group(1))
            package['r_count'] += 1
            continue

        # 処理対象外
        pass

    # 最終パッケージの後処理を行う
    if state is not None and package is not None:
        if package is not None and package['r_count'] > 0:
            summary[state]['packages'].append(copy.deepcopy(package))
            summary[state]['r_sum'] += package['r_count']
            package = None
        summary[state]['p_no'] = p_no
        summary[state]['p_max'] = p_max
        state = None

    return summary

def print_summary(summary, csv_out):
    """
    都道府県毎にサマライズした結果を出力する。
    全体を集計する。
    """
    total = {'count': 0, 'datasets': 0, 'states_check': False, 'resources': 0, 'states': []}
    for state in sorted(list(summary.keys())):
        total = print_summary_state(summary, state, total, csv_out)

    # 都道府県毎のサマライズ結果を出力する
    print_total(total, csv_out)

    # 定義ファイル(crawler.json)のパスを求める
    this_path = os.path.abspath(__file__)
    config_path = os.path.join(os.path.dirname(os.path.dirname(this_path)), \
                               'src', 'crawler.json')
    # 定義ファイルの自治体数と集計結果の自治体数を比較する
    with open(config_path, 'r') as h_config:
        config = json.load(h_config)
        # print('DEBUG:len(config["local_gov"].keys())=' \
        #       + str(len(config['local_gov'].keys())) \
        #       + ', len(total["states"])=' \
        #       + str(len(total["states"])), file=sys.stderr)
        total['states_check'] = len(config['local_gov'].keys()) == len(total['states'])
    # 全体の集計結果を出力する
    csv_out.writerow(['# 総計 自治体数='+str(len(total['states'])), total['datasets'], \
                     str(total['states_check']), total['resources']])

    return total

def print_summary_state(summary, state, total, csv_out):
    """
    指定された都道府県単位のサマライズ情報を出力する。
    """
    # データセットの情報を出力する
    for package in summary[state]['packages']:
        csv_out.writerow([state, package['name'], package['pid'], package['r_count']])

    # 都道府県単位の情報に加算する
    total['count'] += 1
    total['datasets'] += len(summary[state]['packages'])
    total['resources'] += summary[state]['r_sum']
    total['states'].append([
         '# ' + summary[state]['code'] + '_' + summary[state]['name'], \
         str(len(summary[state]['packages'])) \
             + '(' + str(summary[state]['p_no']) \
             + '/' + str(summary[state]['p_max']) + ')', \
         'r_sum=' + str(summary[state]['r_sum']), \
         'check=' + str(summary[state]['p_no']==summary[state]['p_max'])])

    return total

def print_total(total, csv_out):
    """
    都道府県単位の集計情報を出力する。
    """
    for state in total['states']:
        csv_out.writerow(state)

    return

# コマンド呼び出し
if __name__ == '__main__':
    # 初期化
    hlog = None
    rc = 0

    # 出力先と項目見出しを出力する
    csv_out = csv.writer(sys.stdout)
    csv_out.writerow(['自治体名', 'データセット名', 'p_id', 'r_count'])

    # 入力を決定する
    if len(sys.argv) > 1:
        hlog = open(sys.argv[1], 'r')
    else:
        hlog = sys.stdin

    # 実行
    summary = summarize(hlog)
    # print('DEBUG:' + str(summary), file=sys.stderr))
    print_summary(summary, csv_out)

    # オープン入力したファイルをクローズする
    if len(sys.argv) > 1:
        hlog.close()

    # 復帰
    exit(0)

