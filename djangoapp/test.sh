# 調査
# Pythonで逆ジオコーディング【国土地理院API】
#   https://qiita.com/kosei_KB/items/5668bc6522ebe866f291
# 総務省トップ > 政策 > 地方行財政 > 地方行政のデジタル化 > 全国地方公共団体コード
#   https://www.soumu.go.jp/denshijiti/code.html
#
# 緯度・経度から市区町村コードを調べる
wget -O - 'https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress?lat=35.129682381922&lon=138.91838826066135'
#  {"results":{"muniCd":"22206","lv01Nm":"文教町二丁目"}}
#  北海道等の都道府県コードが０で始まる１桁の場合に先頭の０が省略されている模様。
# 市区町村コードから市区町村名を調べる
grep 22206 cache/都道府県コード及び市区町村コード_20190501.csv
#  222062,静岡県,三島市,ｼｽﾞｵｶｹﾝ,ﾐｼﾏｼ
#
# 住所から緯度・経度を取得する
wget -O - 'https://maps.googleapis.com/maps/api/geocode/json?address=静岡県沼津市 中央公園&language=ja&components=country:JP&key=AIzaSyBZa9fI3N-L1OHnkiaGQODmOcPRP-HaWlA'
{
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "中央公園",
               "short_name" : "中央公園",
               "types" : [ "establishment", "park", "point_of_interest", "tourist_attraction" ]
            },
            {
               "long_name" : "１８５−４",
               "short_name" : "１８５−４",
               "types" : [ "premise" ]
            },
            {
               "long_name" : "３",
               "short_name" : "３",
               "types" : [ "political", "sublocality", "sublocality_level_4" ]
            },
            {
               "long_name" : "４丁目",
               "short_name" : "４丁目",
               "types" : [ "political", "sublocality", "sublocality_level_3" ]
            },
            {
               "long_name" : "大手町",
               "short_name" : "大手町",
               "types" : [ "political", "sublocality", "sublocality_level_2" ]
            },
            {
               "long_name" : "沼津市",
               "short_name" : "沼津市",
               "types" : [ "locality", "political" ]
            },
            {
               "long_name" : "静岡県",
               "short_name" : "静岡県",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "日本",
               "short_name" : "JP",
               "types" : [ "country", "political" ]
            },
            {
               "long_name" : "410-0801",
               "short_name" : "410-0801",
               "types" : [ "postal_code" ]
            }
         ],
         "formatted_address" : "日本、〒410-0801 静岡県沼津市大手町４丁目３−１８５−４ 中央公園",
         "geometry" : {
            "location" : {
               "lat" : 35.0987559,
               "lng" : 138.8596195
            },
            "location_type" : "ROOFTOP",
            "viewport" : {
               "northeast" : {
                  "lat" : 35.1001048802915,
                  "lng" : 138.8609684802915
               },
               "southwest" : {
                  "lat" : 35.0974069197085,
                  "lng" : 138.8582705197085
               }
            }
         },
         "partial_match" : true,
         "place_id" : "ChIJJ3iPC2CFGWARMLNJnOF6UoY",
         "plus_code" : {
            "compound_code" : "3VX5+GR 日本、静岡県沼津市",
            "global_code" : "8Q7W3VX5+GR"
         },
         "types" : [ "establishment", "park", "point_of_interest", "tourist_attraction" ]
      }
   ],
   "status" : "OK"
}

# 距離1kmあたりの緯度・経度の度数を計算（日本・北緯35度）　https://easyramble.com/latitude-and-longitude-per-kilometer.html
# 日本での1kmあたりの緯度の大きさ（極半径をもとに計算）
import math
POLE_RADIUS = 6356752.314
lat_degree = ( 360.0 * 1000.0 ) / ( 2.0 * math.pi * POLE_RADIUS )
# 1000m => 0.0090133729745762
# 10m => 0.0001 <= 0.000090133729745762
# 日本での1kmあたりの経度の大きさ（赤道半径をもとに計算）
JAPAN_LATITUDE = 35.0
EQUATOR_RADIUS = 6378137.0
lng_degree = ( 360.0 * 1000.0 ) / ( 2.0 * math.pi * ( EQUATOR_RADIUS * math.cos(JAPAN_LATITUDE * math.pi / 180.0) ) )
# 1000m => 0.010966404715491394
# 10m => 0.0001 <= 0.00010966404715491394

