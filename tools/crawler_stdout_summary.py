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
re_state = re.compile('^([0-9]{1,2}/[0-9]{1,2}) 【([^】]+)】サイト=([0-9]{6}) [^：]+：http')
re_package = re.compile('^([0-9]+)/([0-9]+)\[([^\]]+)\]([^：]+)：(.*)$')
re_make_map = re.compile('^([^\:]+)\:\[([^\]]+)\] マップデータを作成しました。$')

def print_state(state):
    """
    指定された都道府県単位のサマライズ情報を出力する。
    """
    # コメントとして都道府県単位の情報を出力する
    csv_out.writerow([
         '# ' + summary[state]['code'] + '_' + summary[state]['name'], \
         str(len(summary[state]['packages'])) \
             + '(' + str(summary[state]['p_no']) + '/' + str(summary[state]['p_max']) + ')', \
         'r_sum=' + str(summary[state]['r_sum']), \
         'check=' + str(summary[state]['p_no']==summary[state]['p_max'])])
    # データセットの情報を出力する
    for package in summary[state]['packages']:
        csv_out.writerow([state, package['name'], package['pid'], package['r_count']])
    return

csv_out = csv.writer(sys.stdout)
csv_out.writerow(['都道府県名', 'データセット名', 'p_id', 'r_count'])

# 入力を決定する
if len(sys.argv) > 1:
    hlog = open(sys.argv[1], 'r')
else:
    hlog = sys.stdin

# 入力をサマライズする
summary = {}
state = None
package = None
p_no = None
p_max = None
for line in hlog:
    line = line.rstrip()
    m_state = re_state.match(line)
    if m_state is not None:
        # 都道府県の行
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

# オープンしたファイルをクローズする
if len(sys.argv) > 1:
    hlog.close()

# print(str(summary))

# サマライズした結果を出力する
for state in sorted(list(summary.keys())):
    print_state(state)

exit(0)

