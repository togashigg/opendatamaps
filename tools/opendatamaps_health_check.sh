#!/bin/bash
# opendatamaps_health_check.sh: ヘルスチェック
# Usage: opendatamaps_health_check.sh [ホスト[公開名/]]
#          ホスト例：https://opendatamaps.onrender.com/
#          公開名例：opendatamaps
# in /etc/crontab
#   0,12,24,36,48  *  * * *   root    /bin/bash -l /etc/cron.d/opendatamaps_health_check.sh 2>> /var/log/opendatamaps_health_check.log 1>&2

echo -n "$(date '+%Y/%m/%d %H:%M:%S') opendatamaps_health_check.sh start, "
HOST="https://opendatamaps.onrender.com/"
if [ "$1" != "" ]; then
    HOST="$1"
    if [ "${HOST: -1}" != "/" ]; then
        HOST="$HOST/"
    fi
fi
echo "HOST=$HOST"
result_code=0
result_msg="MSG:"
readonly is_true=true
readonly is_false=false
WGET_OPT="wget -qO - --no-check-certificate"

# random delay at cron
if [ "$LOGNAME" == "root" ]; then
    sleep_time=`expr $RANDOM % 64`
    sleep $sleep_time
    echo "$(date '+%Y/%m/%d %H:%M:%S') sleep ended, ${sleep_time}s"
fi

# test1: localitycode-query
if "${is_true}"; then
    test1="OK"
    request="${HOST}api/localitycode/query?code=22206"
    RES_OK='[{"code": "222062", "state_name": "静岡県", "locality_name": "三島市"}]'
    res=`$WGET_OPT "$request"`
    rc=$?
    if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
        test1="NG"
        echo request=$request
        echo rc=$rc
        echo -e "res=$res"
        echo -e "RES_OK=$RES_OK"
        result_code=`expr $result_code + 1`
    fi
    result_msg="$result_msg test1:$test1"
    echo "$(date '+%Y/%m/%d %H:%M:%S') test1: $test1"
fi

# test2: facility-kinds
if "${is_true}"; then
    test2="OK"
    request="${HOST}api/facility/kinds?code=22206"
    RES_OK='{"kinds": ["AED設置箇所", "医療機関", "飲食店・販売店", "介護サービス事業所", "観光施設・場所", "健康", "公園・花壇", "公共施設", "公衆トイレ", "公衆無線LAN", "子育て施設", "指定緊急避難場所", "消防水利施設", "投票所", "避難所", "文化財", "薬局"]}'
    res=`$WGET_OPT "$request"`
    rc=$?
    if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
        test2="NG"
        echo request=$request
        echo rc=$rc
        echo -e "res=$res"
        echo -e "RES_OK=$RES_OK"
        result_code=`expr $result_code + 1`
    fi
    result_msg="$result_msg test2:$test2"
    echo "$(date '+%Y/%m/%d %H:%M:%S') test2: $test2"
fi

# test3: facility-summary
if "${is_true}"; then
    test3="OK"
    request="${HOST}api/facility/summary"
    RES_OK="too big!!"
    RES_OK1='{"code": "222062", "state_name": "静岡県", "locality_name": "三島市", "kinds": [{"AED設置箇所": 96}, {"医療機関": 133}, {"飲食店・販売店": 233}, {"介護サービス事業所": 116}, {"観光施設・場所": 40}, {"健康": 14}, {"公園・花壇": 278}, {"公共施設": 887}, {"公衆トイレ": 48}, {"公衆無線LAN": 34}, {"子育て施設": 70}, {"指定緊急避難場所": 75}, {"消防水利施設": 1602}, {"投票所": 31}, {"避難所": 24}, {"文化財": 92}, {"薬局": 44}]}'
    res=`$WGET_OPT "$request"`
    rc=$?
    res1=`echo -e "$res" | grep -oP '\{"code"\: "222062",( [^ ]+){4} "kinds"\: \[[^\]]*\]\}'`
    if [ "$rc" != "0" -o "$res1" != "$RES_OK1" ]; then
        test3="NG"
        echo request=$request
        echo rc=$rc
        echo -e "res1=$res1"
        echo -e "RES_OK1=$RES_OK1"
        result_code=`expr $result_code + 1`
    fi
    result_msg="$result_msg test3:$test3"
    echo "$(date '+%Y/%m/%d %H:%M:%S') test3: $test3"
fi

# test4: facility-query-center
if "${is_true}"; then
    test4="OK"
    request="${HOST}api/facility/query/center?lat=35.126334&lng=138.9107634&distance=100&kind=公衆無線LAN"
    RES_OK=('[{"locality_code": "222062", "kind": "公衆無線LAN", "dataset": "三島市　公共施設Wi-Fi設置場所", "id": "msm_wifi_10", "label": "三島市総合観光案内所", "lat": 35.125624, "lng": 138.911269, "info": "[{\"id\": \"msm_wifi_10\"}, {\"http://www.w3.org/2000/01/rdf-schema#label\": \"三島市総合観光案内所\"}, {\"URL\": \"http://www.city.mishima.shizuoka.jp/\"}]", "error": null, "distance": 87},' '{"locality_code": "222062", "kind": "公衆無線LAN", "dataset": "三島市　公共施設Wi-Fi設置場所", "id": "msm_wifi_16", "label": "三島駅南口（駅前広場）", "lat": 35.125731, "lng": 138.911418, "info": "[{\"id\": \"msm_wifi_16\"}, {\"http://www.w3.org/2000/01/rdf-schema#label\": \"三島駅南口（駅前広場）\"}, {\"URL\": \"http://izupass.jp/location/detail/303\"}]", "error": null, "distance": 89}]')
    res=`$WGET_OPT "$request"`
    IFS=$'\n'; resa=($res); unset IFS
    rc=$?
    if [[ "$rc" != "0" || "${#resa[@]}" != "${#RES_OK[@]}" \
       || "${resa[0]}" != "${RES_OK[0]}" || "${resa[1]}" != "${RES_OK[1]}" ]]; then
        test4="NG"
        echo request=$request
        echo rc=$rc
        echo -e "res=$res"
        echo -e "RES_OK=${RES_OK[@]}"
        result_code=`expr $result_code + 1`
    fi
    result_msg="$result_msg test4:$test4"
    echo "$(date '+%Y/%m/%d %H:%M:%S') test4: $test4"
fi

# test5: facility-query-locality
if "${is_true}"; then
    test5="OK"
    request="${HOST}api/facility/query/locality?code=22206&kind=公衆トイレ&limit=1"
    RES_OK='[{"locality_code": "222062", "kind": "公衆トイレ", "dataset": "三島市　公衆トイレ設置場所", "id": "msm_tlt_01", "label": "JR三島駅南口", "lat": 35.126013, "lng": 138.912838, "info": "[{\"id\": \"msm_tlt_01\"}, {\"http://www.w3.org/2000/01/rdf-schema#label\": \"JR三島駅南口\"}, {\"use_time\": \"24時間\"}, {\"Multi-Purpose Toilet\": \"有\"}]", "error": null}]'
    res=`$WGET_OPT "$request"`
    rc=$?
    if [ "$rc" != "0" -o "$res" != "$RES_OK" ]; then
        test5="NG"
        echo request=$request
        echo rc=$rc
        echo -e "res=$res"
        echo -e "RES_OK=$RES_OK"
        result_code=`expr $result_code + 1`
    fi
    result_msg="$result_msg test5:$test5"
    echo "$(date '+%Y/%m/%d %H:%M:%S') test5: $test5"
fi

# echo "$result_msg"

if [ "$result_code" != "0" ]; then
    if [ "`which mail`" != "" ]; then
        echo -e "error code = $result_code\ndetails: $result_msg\ncheck: /var/log/opendatamaps_onrender_com_check.log on GCP." \
        | mail -s "ERROR in opendatamaps service on Render!" togashigg@gmail.com
    fi
fi

echo "$(date '+%Y/%m/%d %H:%M:%S') opendatamaps_health_check.sh ended, result=$result_code"
exit $result_code

