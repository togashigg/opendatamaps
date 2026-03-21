#!/bin/bash
# opendatamaps_onrender_com_check.sh: ヘルスチェック

echo "$(date '+%Y/%m/%d %H:%M:%S') opendatamaps_onrender_com_check.sh start."
HOST="https://opendatamaps.onrender.com/"
result_code=0
result_msg="MSG:"
readonly is_true=true
readonly is_false=false

# random delay at cron
if [ "$USER" == "root" ]; then
    sleep_time=`expr $RANDOM % 60 + 1`
    sleep $sleep_time
fi

# test1: localitycode
test1="OK"
RES_OK="[{\"code\": \"222062\", \"state_name\": \"静岡県\", \"locality_name\": \"三島市\"}]"
res=`wget -qO - "${HOST}api/localitycode/query?code=22206"`
rc=$?
if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
    test1="NG"
    echo request="${HOST}api/facility/kinds?code=22206"
    echo rc=$rc
    echo res=$res
    echo correct=$RES_OK
    result_code=`expr $result_code + 1`
fi
echo "test1: $test1"
result_msg="$result_msg test1:$test1"

# test2: facility-kinds
if "${is_false}"; then
    test2="OK"
    RES_OK="{\"kinds\": [\"AED設置箇所\", \"医療機関\", \"飲食店・販売店\", \"介護サービス事業所\", \"観光施設・場所\", \"健康\", \"公園・花壇\", \"公共施設\", \"公衆トイレ\", \"公衆無線LAN\", \"子育て施設\", \"指定緊急避難場所\", \"消防水利施設\", \"投票所\", \"避難所\", \"文化財\", \"薬局\"]}"
    res=`wget -qO - "${HOST}api/facility/kinds?code=22206"`
    rc=$?
    if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
        test2="NG"
        echo request="${HOST}api/facility/kinds?code=22206"
        echo rc=$rc
        echo res=$res
        echo correct=$RES_OK
        result_code=`expr $result_code + 1`
    fi
    echo "test2: $test2"
    result_msg="$result_msg test2:$test2"
fi

# test3: facility-summary
if "${is_false}"; then
    test3="OK"
    res=`wget -qO - "${HOST}api/facility/summary"`
    rc=$?
    if [ "$rc" != "0" ]; then
        test3="NG"
        echo request="${HOST}api/facility/kinds?code=22206"
        echo rc=$rc
        echo res=$res
        echo correct=$RES_OK
        result_code=`expr $result_code + 1`
    fi
    echo "test3: $test3"
    result_msg="$result_msg test3:$test3"
fi

# test4: facility-query-center
test4="OK"
RES_OK="[{\"locality_code\": \"222062\", \"kind\": \"公衆無線LAN\", \"dataset\": \"三島市　公共施設Wi-Fi設置場所\", \"id\": \"msm_wifi_10\", \"label\": \"三島市総合観光案内所\", \"lat\": 35.125624, \"lng\": 138.911269, \"info\": \"[{\\\"id\\\": \\\"msm_wifi_10\\\"}, {\\\"http://www.w3.org/2000/01/rdf-schema#label\\\": \\\"三島市総合観光案内所\\\"}, {\\\"URL\\\": \\\"http://www.city.mishima.shizuoka.jp/\\\"}]\", \"error\": null, \"distance\": 87}, {\"locality_code\": \"222062\", \"kind\": \"公衆無線LAN\", \"dataset\": \"三島市　公共施設Wi-Fi設置場所\", \"id\": \"msm_wifi_16\", \"label\": \"三島駅南口（駅前広場）\", \"lat\": 35.125731, \"lng\": 138.911418, \"info\": \"[{\\\"id\\\": \\\"msm_wifi_16\\\"}, {\\\"http://www.w3.org/2000/01/rdf-schema#label\\\": \\\"三島駅南口（駅前広場）\\\"}, {\\\"URL\\\": \\\"http://izupass.jp/location/detail/303\\\"}]\", \"error\": null, \"distance\": 89}]"
res=`wget -qO - "${HOST}api/facility/query/center?lat=35.126334&lng=138.9107634&distance=100&kind=公衆無線LAN"`
rc=$?
if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
    test4="NG"
    echo request="${HOST}api/facility/kinds?code=22206"
    echo rc=$rc
    echo res=$res
    echo correct=$RES_OK
    result_code=`expr $result_code + 1`
fi
echo "test4: $test4"
result_msg="$result_msg test4:$test4"

# test5: facility-query-locality
test5="OK"
RES_OK="[{\"locality_code\": \"222062\", \"kind\": \"公衆無線LAN\", \"dataset\": \"三島市　公共施設Wi-Fi設置場所\", \"id\": \"msm_wifi_01\", \"label\": \"図書館\", \"lat\": 35.123374, \"lng\": 138.915486, \"info\": \"[{\\\"id\\\": \\\"msm_wifi_01\\\"}, {\\\"http://www.w3.org/2000/01/rdf-schema#label\\\": \\\"図書館\\\"}, {\\\"URL\\\": \\\"http://tosyokan.city.mishima.shizuoka.jp/top\\\"}]\", \"error\": null}]"
res=`wget -qO - "${HOST}api/facility/query/locality?code=222062&kind=公衆無線LAN&limit=1"`
rc=$?
if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
    test5="NG"
    echo request="${HOST}api/facility/query/locality?code=222062&kind=公衆無線LAN&limit=1"
    echo rc=$rc
    echo res=$res
    echo correct=$RES_OK
    result_code=`expr $result_code + 1`
fi
echo "test5: $test5"
result_msg="$result_msg test5:$test5"
# echo "$result_msg"

if [ "`which mail`" != "" ]; then
    echo -e "error code = $result_code\ndetails: $result_msg\ncheck: opendatamaps_onrender_com_check.log on GCP." \
    | mail -s "ERROR in opendatamaps service on Render!" togashigg@gmail.com
fi

echo "$(date '+%Y/%m/%d %H:%M:%S') opendatamaps_onrender_com_check.sh ended, result=$result_code"
exit $result_code

