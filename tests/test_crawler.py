#!/usr/bin/env python3
# test_crawler.py: crawler.py用ユニットテスト

import os
import sys
import shutil
import unittest
from logging import basicConfig, DEBUG	# DEBUGログを参照したい場合

package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if package_path not in sys.path:
    sys.path.append(package_path)
src_path = os.path.join(package_path, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from src import crawler

tests_path = os.path.join(package_path, 'tests')
answer_path = os.path.join(tests_path, 'answer')

class TestCrawler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # テストクラス初期化
        pass

    @classmethod
    def tearDownClass(cls):
        # テストクラス破棄
        pass

    def setUp(self):
        # テスト初期化
        pass

    def tearDown(self):
        # テスト終了
        pass

    def test___init___001(self):
        """
        コンストラクタのテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 正常系：全パラメタ省略、復帰値無し
        testobj = None
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        print('クラス変数={')
        print('.APP_DIR='+testobj.APP_DIR)
        print('.settings_path='+testobj.settings_path)
        print('.LOCALITY_CODE_FILE='+testobj.LOCALITY_CODE_FILE)
        print('.LOCALITY_CODE_PATH='+testobj.LOCALITY_CODE_PATH)
        print('.IGNORE_WORD_IN_DATASET_NAME='+str(testobj.IGNORE_WORD_IN_DATASET_NAME))
        print('.KIND_LIST_NORMALIZED_RE.keys()='+str(testobj.KIND_LIST_NORMALIZED_RE.keys()))
        print('.OPENDATA_SITES='+str(testobj.OPENDATA_SITES))
        print('.site_names='+str(testobj.site_names))
        print('.download_dir='+testobj.download_dir)
        print('.cache_dir='+testobj.cache_dir+' }')
        # ToDo: check?
        # pwd = subprocess.run('pwd',capture_output=True, text=True).stdout
        # with open(os.path.join(answer_path, testid), 'r') as hfa:
        #     answer = eval(hfa.read())
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test___del___001(self):
        """
        デストラクタのテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 正常系：パラメタ無し・復帰値無し
        testobj.__del__()
        self.assertEqual(True, True)
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_names_001(self):
        """
        サイト名リスト取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ指定、raise TypeError
        try:
            rc = testobj.get_names('error')
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 正常系：パラメタ無し、復帰値=サイト名リスト
        rc = testobj.get_names()
        self.assertEqual(type(rc) is list, True)
        self.assertEqual(rc, ["東京都", "静岡県"])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_site_info_001(self):
        """
        サイト情報取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_site_info()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ name=None、raise Exception
        try:
            rc = testobj.get_site_info(None)
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'nameパラメタ（自治体名）を指定してください。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ name='未知'、raise Exception
        try:
            rc = testobj.get_site_info('未知')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定された自治体名が存在しません。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ name='静岡県'、復帰値=サイト情報
        site_info = testobj.get_site_info('静岡県')
        self.assertTrue(type(site_info) is dict)
        self.assertEqual(site_info['name'], '静岡県')
        # print('site_info='+str(rc))
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_cache_initialize(self):
        """
        キャッシュ初期化関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_packageids_in_site()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ site_info=None、raise Exception
        try:
            rc = testobj.get_packageids_in_site(None)
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info=''、raise Exception
        try:
            rc = testobj.get_packageids_in_site('')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={}、raise Exception
        try:
            rc = testobj.get_packageids_in_site('')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ site_info=<静岡県のサイト情報>、復帰値=0
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        # print('testobj=', vars(testobj))
        print('testobj.cache_site_dir='+str(testobj.cache_site_dir))
        print('testobj.locality_dict=', len(testobj.locality_dict))
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_packageids_in_site_001(self):
        """
        サイトのパッケージID一覧取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_packageids_in_site()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ site_info=None、raise Exception
        try:
            rc = testobj.get_packageids_in_site(None)
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info=''、raise Exception
        try:
            rc = testobj.get_packageids_in_site('')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={}、raise Exception
        try:
            rc = testobj.get_packageids_in_site('')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ site_info=<静岡県のサイト情報>、復帰値=パッケージ一覧
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertTrue(packageids==answer)
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_package_info_001(self):
        """
        パッケージ情報取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_package_info()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ1つ、raise TypeError
        try:
            rc = testobj.get_package_info({'name':'静岡県'})
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ site_info=None, packageid='ID'、raise Exception
        try:
            rc = testobj.get_package_info(None, 'ID')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info='', packageid='ID'、raise Exception
        try:
            rc = testobj.get_package_info('', 'ID')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={}, packageid='ID'、raise Exception
        try:
            rc = testobj.get_package_info({}, 'ID')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたサイト定義が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={'name':'静岡県'}, packageid=None、raise Exception
        try:
            rc = testobj.get_package_info({'name':'静岡県'}, None)
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージIDが誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={'name':'静岡県'}, packageid=1、raise Exception
        try:
            rc = testobj.get_package_info({'name':'静岡県'}, 1)
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージIDが誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ site_info={'name':'静岡県'}, packageid=''、raise Exception
        try:
            rc = testobj.get_package_info({'name':'静岡県'}, '')
            print('rc='+str(rc))
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージIDが誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ site_info=<サイト情報>, packageid='...'、復帰値=パッケージ情報
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            self.assertTrue(package, answer[p])
            # print('  ('+str(p)+') answer ='+str(answer[p]))
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_select_package_info_001(self):
        """
        パッケージ情報の正当性チェック関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.select_package_info()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        """ 見直し↓
        # 異常系：パラメタ package_info=None、raise Exception
        try:
            rc = testobj.select_package_info(None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info=''、raise Exception
        try:
            rc = testobj.select_package_info('')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info={}、raise Exception
        try:
            rc = testobj.select_package_info({})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報が誤りです。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info={'success':False}、raise Exception
        try:
            rc = testobj.select_package_info({'success':False, 'result':[]})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報は異常です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info={'success':True}、raise Exception
        try:
            rc = testobj.select_package_info({'success':True})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報は異常です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info={'success':True, 'result':{}}、raise Exception
        try:
            rc = testobj.select_package_info({'success':True, 'result':{}})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報は異常です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ package_info={'success':True, 'result':{'resources':1}}、raise Exception
        try:
            rc = testobj.select_package_info({'success':True, 'result':{'resources':1}})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたパッケージ情報は異常です。')
            print('OK', e.__class__.__name__+':', e)
        ### ↑ここまで """
        # 正常系：パラメタ package_info={'success':True, 'result':{'resources':[]}}
        rc = testobj.select_package_info({'code':'222062'}, 'packageid', {
                'success':True, 
                'result': {
                    'name': '○○県○○市AED設置場所',
                    'resources':[]
                }
        })
        self.assertEqual(rc, None)
        # 正常系：パラメタ package_info={'success':True, 'result':{'resources':[]}}
        rc = testobj.select_package_info({'code':'222062'}, 'packageid', {
                'success':True, 
                'result': {
                    'name': '○○県○○市AED設置場所',
                    'title': '○○県○○市公衆無線LANアクセスポイント設置場所',
                    'resources':[]
                }
        })
        self.assertEqual(rc, None)
        # 正常系：パラメタ package_info={'success':True, 'result':{'resources':[]}}
        rc = testobj.select_package_info({'code':'222062'}, 'packageid', {
                'success':True, 
                'result': {
                    'name': '備品台帳',
                    'resources':[]
                }
        })
        self.assertEqual(rc, '備品台帳：種別が特定できないか無視対象です。[]')
        # 正常系：パラメタ package_info={'success':True, 'result':{'resources':[]}}
        rc = testobj.select_package_info({'code':'222062'}, 'packageid', {
                'success':True, 
                'result': {
                    'name': '○○県○○市病院や公共施設に関するデータ',
                    'resources':[]
                }
        })
        self.assertEqual(rc, '○○県○○市病院や公共施設に関するデータ：特定単語を含むデータセットは除外。公共施設に関するデータ')
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_package_title_001(self):
        """
        パッケージ情報からタイトル取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_package_title()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 正常系：パラメタ package=パッケージ情報、復帰値=タイトル
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            title = testobj.get_package_title(package)
            # print('    title='+str(title))
            self.assertEqual(title, answer[p])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_package_kind_001(self):
        """
        パッケージのタイトルから種別取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_package_kind()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 正常系：パラメタ package=タイトル、復帰値=種別
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            title = testobj.get_package_title(package)
            # print('    title='+str(title))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            self.assertEqual(kind, answer[p])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_all_resources_001(self):
        """
        パッケージ情報から全リソース情報取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_all_resources()
            print('rc='+str(rc))
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 正常系：パラメタ package=パッケージ情報、復帰値=リソースリスト
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            for resource in resources:
                del resource['_package_']
            self.assertEqual(resources, answer[p])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_valid_resources_001(self):
        """
        有効なリソース一覧取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_valid_resources()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resources=None、raise Exception
        try:
            rc = testobj.get_valid_resources(None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたリソース一覧は異常です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resources=''、raise Exception
        try:
            rc = testobj.get_valid_resources('')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], '指定されたリソース一覧は異常です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resources=[1]、raise Exception
        try:
            rc = testobj.get_valid_resources([1])
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'リソースはdict型で指定して下さい。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resources=[]、raise Exception
        rc = testobj.get_valid_resources([])
        self.assertEqual(rc, [])
        # 正常系：パラメタ resources=[{}]、復帰値=[]
        rc = testobj.get_valid_resources([{}])
        self.assertEqual(rc, [])
        # 正常系：パラメタ resources=リソースリスト、復帰値=リソースリスト
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            for r in valid:
                del r['_package_']
            self.assertEqual(valid, answer[p])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_get_content_by_resource_001(self):
        """
        リソースの内容取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.get_content_by_resource()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.get_content_by_resource([])
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ kind=None, resource={}、raise Exception
        try:
            rc = testobj.get_content_by_resource(None, {})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ kind=1, resource={}、raise Exception
        try:
            rc = testobj.get_content_by_resource(1, {})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ kind='無効な種別', resource={}、raise Exception
        try:
            rc = testobj.get_content_by_resource('無効な種別', {})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ kind='公衆トイレ', resource=None、raise Exception
        try:
            rc = testobj.get_content_by_resource('公衆トイレ', None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ kind='公衆トイレ', resource=1、raise Exception
        try:
            rc = testobj.get_content_by_resource('公衆トイレ', 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ kind='公衆トイレ', resource={}、raise Exception
        try:
            rc = testobj.get_content_by_resource('公衆トイレ', {})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ kind=<有効な値>, resource=<有効なリソース定義>、復帰値=内容
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                # print('    ('+str(r)+')', str(resource))
                resource = testobj.get_content_by_resource(kind, resource)
                # print('    ('+str(p)+') ('+str(r)+')', str(kind), \
                #         'resource='+str(resource))
                with open(os.path.join(answer_path, \
                        testid+'_'+str(p)+'_'+str(r)), 'rb') as hfa:
                    answer_content = hfa.read()
                self.assertEqual(resource['_content_'], answer_content)
                # print('    content_'+str(p)+'_'+str(r)+': OK')
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_check_html_page_001(self):
        """
        リソース内容がHTMLである場合はリンク先の内容取得関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.check_html_page()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.check_html_page({})
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resource=None, dir=''、raise Exception
        try:
            rc = testobj.check_html_page(None, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource=1, dir=''、raise Exception
        try:
            rc = testobj.check_html_page(1, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={}, dir=None、raise Exception
        try:
            rc = testobj.check_html_page({}, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_content_':' '}, dir=None、raise Exception
        try:
            rc = testobj.check_html_page({'_content_':' '}, None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_content_':' '}, dir=1、raise Exception
        try:
            rc = testobj.check_html_page({'_content_':' '}, 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_content_':' '}, dir=''、raise Exception
        try:
            rc = testobj.check_html_page({'_content_':' '}, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_content_':' '}, dir='/__nothing__'、raise Exception
        try:
            rc = testobj.check_html_page({'_content_':' '}, '/__nothing__')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容 
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                # print('    ('+str(r)+')', str(resource)[:64])
                # print('    ('+str(r)+')', str(resource['format']), str(resource['name']),
                #         str(resource['url']), str(resource['filename']))
                resource = testobj.get_content_by_resource(kind, resource)
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                if '_redirect_' in resource and resource['_redirect_'] is not None:
                    pass
                    print('    ('+str(r)+')', str(resource['format']), str(resource['name']), \
                            str(resource['url']), str(resource['filename']))
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_check_content_format_001(self):
        """
        コンテンツの内容でformat検査関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.check_content_format()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.check_content_format({})
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resource=None, dir=''、raise Exception
        try:
            rc = testobj.check_content_format(None, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource=1, dir=''、raise Exception
        try:
            rc = testobj.check_content_format(1, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':1}, dir=None、raise Exception
        try:
            rc = testobj.check_content_format({'format':1}, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':1}, dir=None、raise Exception
        try:
            rc = testobj.check_content_format({'format':' ', 'filename':1}, None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' '}, dir=1、raise Exception
        try:
            rc = testobj.check_content_format({'format':' ', 'filename':' '}, 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' '}, dir='/__nothing__'、
        #                  raise Exception
        try:
            rc = testobj.check_content_format({'format':' ', 'filename':' '}, '/__nothing__')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容 
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                # print('    ('+str(r)+')', str(resource)[:64])
                # print('    ('+str(r)+')', str(resource['format']), str(resource['name']),
                #         str(resource['url']), str(resource['filename']))
                resource = testobj.get_content_by_resource(kind, resource)
                result = [resource['format'], resource['filename']]
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_content_format(resource, testobj.package_dir)
                # print('    ('+str(r)+')', str(resource['format']), str(resource['name']),
                #         str(resource['url']), str(resource['filename']))
                result.extend([resource['format'], resource['filename']])
                self.assertEqual(result, answer[p][r])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_content_to_table_001(self):
        """
        コンテンツをテーブル形式変換関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.content_to_table()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.content_to_table({})
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resource=None, dir=' '、raise Exception
        try:
            rc = testobj.content_to_table(None, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource=1, dir=''、raise Exception
        try:
            rc = testobj.content_to_table(1, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={}, dir=' '、raise Exception
        try:
            rc = testobj.content_to_table({}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':1}, dir=' '、raise Exception
        try:
            rc = testobj.content_to_table({'format':1}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':1}, dir=' '、raise Exception
        try:
            rc = testobj.content_to_table({'format':' ', 'filename':1}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' '}, dir=' '、raise Exception
        try:
            rc = testobj.content_to_table({'format':' ', 'filename':' '}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' ', '_content_':None}, 
        #                  dir=' '、raise Exception
        try:
            rc = testobj.content_to_table({'format':' ', 'filename':' ', '_content_':None}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' ', '_content_':' '}, 
        #                  dir=1、raise Exception
        try:
            rc = testobj.content_to_table({'format':' ', 'filename':' ', '_content_':' '}, 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'format':' ', 'filename':' ', '_content_':' '}, 
        #                  dir='/__nothing__'、raise Exception
        try:
            rc = testobj.content_to_table({'format':' ', 'filename':' ', '_content_':' '}, \
                    '/__nothing__')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                # print('    ('+str(r)+')', str(resource)[:64])
                # print('    ('+str(r)+')', str(resource['format']), str(resource['name']),
                #         str(resource['url']), str(resource['filename']))
                resource = testobj.get_content_by_resource(kind, resource)
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_content_format(resource, testobj.package_dir)
                # self.assertEqual(result, answer[p][r])
                resource = testobj.content_to_table(resource, testobj.package_dir)
                # print('    ('+str(p)+') ('+str(r)+') table='+str(resource['_table_']))
                with open(os.path.join(answer_path, \
                        testid+'_'+str(p)+'_'+str(r)), 'r') as hfa: 
                    answer = eval(hfa.read())
                self.assertEqual(resource['_table_'], answer)
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_make_map_from_table_001(self):
        """
        表形式の項目名からマップ情報作成関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.make_map_from_table()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resource=None, kind=' '、raise Exception
        try:
            rc = testobj.make_map_from_table(None, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource=1, kind=' '、raise Exception
        try:
            rc = testobj.make_map_from_table(1, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={}, kind=' '、raise Exception
        try:
            rc = testobj.make_map_from_table({}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':1}, kind=' '、raise Exception
        try:
            rc = testobj.make_map_from_table({'_table_':1}, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[]}, kind=None、raise Exception
        try:
            rc = testobj.make_map_from_table({'_table_':[]}, None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[]}, kind=1、raise Exception
        try:
            rc = testobj.make_map_from_table({'_table_':[]}, 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[]}, kind=''、raise Exception
        try:
            rc = testobj.make_map_from_table({'_table_':[]}, '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[]}, kind='__未定義__'、raise Exception
        try:
            rc = testobj.make_map_from_table({'_table_':[]}, '__未定義__')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'kindパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        with open(os.path.join(answer_path, testid), 'r') as hfa:
            answer = eval(hfa.read())
        self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            valid = testobj.get_valid_resources(resources)
            kind = testobj.get_package_kind(package)
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                resource = testobj.get_content_by_resource(kind, resource)
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_content_format(resource, testobj.package_dir)
                resource = testobj.content_to_table(resource, testobj.package_dir)
                self.assertTrue(resource != None)
                resource = testobj.make_map_from_table(resource, kind)
                # print('  ('+str(p)+') ('+str(r), 'map='+str(resource['_map_']))
                self.assertEqual(resource['_map_'], answer[p][r])
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_table_to_mapdata_001(self):
        """
        テーブルデータをマップデータ(JSON形式)変換関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.table_to_mapdata()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ resource=None、raise Exception
        try:
            rc = testobj.table_to_mapdata(None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource=1、raise Exception
        try:
            rc = testobj.table_to_mapdata(1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={}、raise Exception
        try:
            rc = testobj.table_to_mapdata({})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':1}、raise Exception
        try:
            rc = testobj.table_to_mapdata({'_table_':1})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[]}、raise Exception
        try:
            rc = testobj.table_to_mapdata({'_table_':[]})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ resource={'_table_':[], '_map_':1}、raise Exception 
        try:
            rc = testobj.table_to_mapdata({'_table_':[], '_map_':1})
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'resourceパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        for p, packageid in enumerate(packageids):
            # print('  ('+str(p)+')', packageid)
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            # print('  ('+str(p)+') package='+str(package))
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            # print('  ('+str(p)+') answer ='+str(answer[p]))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            # print('    resources='+str(resources))
            valid = testobj.get_valid_resources(resources)
            # print('    valid='+str(valid))
            kind = testobj.get_package_kind(package)
            # print('    kind='+str(kind))
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                # print('    ('+str(r)+')', str(resource)[:64])
                # print('    ('+str(r)+')', str(resource['format']), str(resource['name']),
                #         str(resource['url']), str(resource['filename']))
                resource = testobj.get_content_by_resource(kind, resource)
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_content_format(resource, testobj.package_dir)
                # self.assertEqual(result, answer[p][r])
                resource = testobj.content_to_table(resource, testobj.package_dir)
                self.assertTrue(resource != None)
                resource = testobj.make_map_from_table(resource, kind)
                if resource['_map_'] == {}:
                    continue
                map_data = testobj.table_to_mapdata(resource)
                # print('  ('+str(p)+') ('+str(r)+')', 'map_data='+str(map_data))
                # print('    file='+testid+'_'+str(p)+'_'+str(r))
                with open(os.path.join(answer_path, \
                        testid+'_'+str(p)+'_'+str(r)), 'r') as hfa:
                    answer = eval(hfa.read())
                self.assertEqual(map_data, answer)
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

    def test_save_to_cache_001(self):
        """
        マップデータ（JSON形式）をキャッシュ保存関数のテスト
        """
        testid = sys._getframe().f_code.co_name
        print('[[['+testid+']]]')
        # 環境設定
        testobj = crawler.Crawler()
        self.assertEqual(type(testobj) is crawler.Crawler, True)
        # 異常系：パラメタ無し、raise TypeError
        try:
            rc = testobj.save_to_cache()
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.save_to_cache({})
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ不足、raise TypeError
        try:
            rc = testobj.save_to_cache({}, dir=' ')
            self.assertTrue(False)
        except TypeError as e:
            print('OK', e.__class__.__name__+':', e)
        except Exception as e:
            print('ERROR', e.__class__.__name__+':', e)
            self.assertTrue(False)
        # 異常系：パラメタ mapping_data=None, file=' '、raise Exception
        try:
            rc = testobj.save_to_cache(None, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'mapping_dataパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=1, file=' '、raise Exception
        try:
            rc = testobj.save_to_cache(1, ' ')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'mapping_dataパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=[], file=None、raise Exception
        try:
            rc = testobj.save_to_cache([], None)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'fileパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=[], file=1、raise Exception
        try:
            rc = testobj.save_to_cache([], 1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'fileパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=[], file=''、raise Exception
        try:
            rc = testobj.save_to_cache([], '')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'fileパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=[], file=' ', dir=1、raise Exception
        try:
            rc = testobj.save_to_cache([], ' ', dir=1)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 異常系：パラメタ mapping_data=[], file=' ', dir=''、raise Exception
        try:
            rc = testobj.save_to_cache([], ' ', dir='')
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.args[0], 'dirパラメタは無効な値です。')
            print('OK', e.__class__.__name__+':', e)
        # 正常系：パラメタ resource=<有効な値>, dir=<有効な値>、復帰値=内容
        site_info = testobj.get_site_info('静岡県')
        # print('site_info='+str(site_info))
        self.assertEqual(isinstance(site_info, dict), True)
        self.assertEqual(site_info['name'], '静岡県')
        rc = testobj.cache_initialize(site_info)
        self.assertEqual(rc, 0)
        packageids = testobj.get_packageids_in_site(site_info)
        # print('packageids='+str(packageids))
        self.assertEqual(isinstance(packageids, list), True)
        self.assertEqual(packageids[0], '003a6dde-9eef-455e-9e00-91d70643f4af')
        self.assertEqual(packageids[-1], 'ffeff0d5-fd7b-4e63-b96f-bdd198e64f4e')
        # with open(os.path.join(answer_path, testid), 'r') as hfa:
        #     answer = eval(hfa.read())
        # self.assertEqual(len(packageids), len(answer))
        for p, packageid in enumerate(packageids):
            package = testobj.get_package_info(site_info, packageid)
            if package is None:
                continue
            self.assertTrue(package['help'][-17:] == 'name=package_show')
            self.assertTrue(package['success'] == True)
            self.assertTrue(isinstance(package['result']['resources'], list))
            rc = testobj.select_package_info(site_info, packageid, package)
            if rc is not None:
                continue
            resources = testobj.get_all_resources(package)
            valid = testobj.get_valid_resources(resources)
            kind = testobj.get_package_kind(package)
            if kind is None:
                continue
            for r, resource in enumerate(valid):
                resource = testobj.get_content_by_resource(kind, resource)
                self.assertTrue('_content_' in resource)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_html_page(resource, testobj.package_dir)
                self.assertNotEqual(resource, None)
                self.assertNotEqual(resource['_content_'], None)
                resource = testobj.check_content_format(resource, testobj.package_dir)
                resource = testobj.content_to_table(resource, testobj.package_dir)
                self.assertTrue(resource != None)
                resource = testobj.make_map_from_table(resource, kind)
                if resource['_map_'] == {}: 
                    continue
                map_data = testobj.table_to_mapdata(resource)
                save_path = testobj.save_to_cache(map_data, testid+'_'+str(r),
                        dir=packageid)
                # print('  ('+str(p)+') ('+str(r)+')', 'save_path='+str(save_path))
                self.assertEqual(save_path.split('/')[-2], packageid)
                self.assertEqual(save_path.split('/')[-1], testid+'_'+str(r))
        print('[[['+testid+':OK]]]')
        # 終了
        testobj = None

# コマンド実行
if __name__ == "__main__":
    # basicConfig(level=DEBUG, stream=sys.stdout)	# DEBUGログを参照する場合
    os.environ['BASE_DIR'] = tests_path			# tests/下のdownload/cacheを使う
    unittest.main()

