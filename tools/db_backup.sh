#!/bin/bash
# db_badkup.sh DB内全テーブルをバックアップする。
# Usage: db_backup.sh
#   Docker運用ディレクトリで実行すること。
#   以下の環境変数を定義すること。
#   ・POSTGRESQL_USER
#   ・POSTGRESQL_DBNAME
# 備考：バックアップ・リストア専用DBサービスを使用するため、以下の手順で実行する。
#   1. 通常サービスを停止する
#   2. バックアップ・リストア専用DBサービスを起動する
#   3. バックアップを実行する
#   4. バックアップ・リストア専用DBサービスを停止する
#   5. 通常サービスを起動する

DOCKER_COMPOSE_DIR="."
DATETIME="$(date '+%Y%m%d%H%M%S')"
DB_DIR="$DOCKER_COMPOSE_DIR/db"
DB_BACKUP="$DB_DIR/db_backup_$DATETIME.gz"
DB_LOG="$DB_DIR/db_backup_$DATETIME.log"
PRINT_LOG='tail -n +$LOG_L $DB_LOG; LOG_L=$((`wc -l $DB_LOG | cut -d " " -f 1` + 1)); echo "..."'
LOG_L="1"
RESTART_FLAG="1"

echo "$(date '+%Y/%m/%d %H:%M:%S') db_backup.sh start." > $DB_LOG
echo "  docker-compose directory: $DOCKER_COMPOSE_DIR" >> $DB_LOG
echo "  backup file: $DB_BACKUP" >> $DB_LOG
echo "  log    file: $DB_LOG" >> $DB_LOG

echo "# docker-compose down" >> $DB_LOG
eval $PRINT_LOG
DOCKER_PS=`docker-compose ps | grep "docker_db_1" | wc -l`
if [ $DOCKER_PS -gt 0 ]; then
    docker-compose down >> $DB_LOG 2>&1
    echo "docker-compose down ended, rc=$?" >> $DB_LOG
else
    echo "already stopped." >> $DB_LOG
    RESTART_FLAG="0"
fi

echo "# docker-compose -f docker-compose.yml.db up -d" >> $DB_LOG
eval $PRINT_LOG
docker-compose -f docker-compose.yml.db up -d >> $DB_LOG 2>&1
echo "docker-compose -f docker-compose.yml.db up -d ended, rc=$?" >> $DB_LOG
sleep 5	# wait for safety

echo "# print database information." >> $DB_LOG
eval $PRINT_LOG
docker exec -i docker_db_1 psql -qV $POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG
docker exec -i docker_db_1 psql -q \
	-c "\\d localitycode" $POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG
docker exec -i docker_db_1 psql -q \
	-c "SELECT COUNT(*) AS "レコード数" FROM localitycode;" \
	$POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG
docker exec -i docker_db_1 psql -q \
	-c "\\d opendatamaps" $POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG
docker exec -i docker_db_1 psql -q \
        -c "SELECT COUNT(*) AS "レコード数" FROM opendatamaps;" \
        $POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG
docker exec -i docker_db_1 psql -q \
	-c "SELECT MAX(l.state_name) AS "都道府県名",COUNT(*) AS "レコード数" \
		FROM opendatamaps o JOIN localitycode l ON o.locality_code = l.code \
		GROUP BY l.state_name ORDER BY l.state_name;" \
	$POSTGRESQL_DBNAME $POSTGRESQL_USER >> $DB_LOG

echo "# docker exec -i docker_db_1 pg_dump -U \$POSTGRESQL_USER \$POSTGRESQL_DBNAME" >> $DB_LOG
eval $PRINT_LOG
(docker exec -i docker_db_1 pg_dump -U $POSTGRESQL_USER $POSTGRESQL_DBNAME \
	2>> $DB_LOG; echo "pg_dump rc=$?" >> $DB_LOG) | gzip > $DB_BACKUP
rc=`tail -1 $DB_LOG | cut -d "=" -f 2`

echo "# docker-compose down" >> $DB_LOG
eval $PRINT_LOG
docker-compose down >> $DB_LOG 2>&1
echo "docker-compose down ended, rc=$?" >> $DB_LOG

if [ "$RESTART_FLAG" == "1" ]; then
    echo "# docker-compose up -d" >> $DB_LOG
    eval $PRINT_LOG
    docker-compose up -d >> $DB_LOG 2>&1
    echo "docker-compose up -d ended, rc=$?" >> $DB_LOG
fi

echo "$(date '+%Y/%m/%d %H:%M:%S') db_backup.sh ended, rc=$rc" >> $DB_LOG
tail -n +$LOG_L $DB_LOG

exit $rc

