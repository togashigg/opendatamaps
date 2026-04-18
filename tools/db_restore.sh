#!/bin/bash
# db_restore.sh DB内全テーブルをリストアする。
# Usage: db_restore.sh [バックアップファイルパス]
#   Docker運用ディレクトリで実行すること。
#   バックアップファイルおよびバックアップログをdbディレクトリ下に配置すること。
#   以下の環境変数を定義すること。
#   ・POSTGRESQL_USER
#   ・POSTGRESQL_DBNAME
# 備考：バックアップ・リストア専用DBサービスを使用するため、以下の手順で実行する。
#   1. 通常サービスを停止する
#   2. バックアップ・リストア専用DBサービスを起動する
#   3. 現状のスキーマを削除して空のスキーマを作成する
#   4. リストアを実行する
#   5. バックアップ・リストア専用DBサービスを停止する
#   6. 通常サービスを起動する
#   7. バックアップ情報とリストア情報をチェックする

DOCKER_COMPOSE_DIR="."
DATETIME="$(date '+%Y%m%d%H%M%S')"
DB_DIR="$DOCKER_COMPOSE_DIR/db"
DB_LOG="$DB_DIR/db_restore_$DATETIME.log"
PRINT_LOG='tail -n +$LOG_L $DB_LOG; LOG_L=$((`wc -l $DB_LOG | cut -d " " -f 1` + 1)); echo "..."'
LOG_L="1"
RESTART_FLAG="1"

DB_BACKUP="$1"
if [ "$1" == "" ]; then
    if [ `(cd $DB_DIR; ls db_backup_*.gz) | wc -l` -lt 1 ]; then
        echo "ERROR: backup file not fount."
        exit 11
    fi
    backup_file=`(cd $DB_DIR; ls -tr db_backup_*.gz) | tail -n 1`
    backup_log="${backup_file%.*}.log"
    if [ ! -f "$DB_DIR/$backup_log" ]; then
        echo "ERROR: backup log not found, log=$DB_DIR/$backup_log"
        exit 12
    fi
    DB_BACKUP="$DB_DIR/$backup_file"
fi
DB_BACKUP_LOG="${DB_BACKUP%.*}.log"
if [ ! -f "$DB_BACKUP_LOG" ]; then
    echo "ERROR: backup log not found, log=$DB_BACKUP_LOG"
    exit 12
fi

echo "$(date '+%Y/%m/%d %H:%M:%S') db_restore.sh start." > $DB_LOG
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

echo "# psql -U \$POSTGRESQL_USER \$POSTGRESQL_DBNAME (recreate SCHEMA public)" >> $DB_LOG
eval $PRINT_LOG
docker exec -i docker_db_1 psql -U $POSTGRESQL_USER $POSTGRESQL_DBNAME << EOS >> $DB_LOG 2>&1
SELECT current_schema;
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
EOS
rc=$?
echo "DROP and CREATE SCHEMA public ended, rc=$rc" >> $DB_LOG

echo "# gzip -cd $DB_BACKUP | psql -U \$POSTGRESQL_USER \$POSTGRESQL_DBNAME" >> $DB_LOG
eval $PRINT_LOG
echo "..."
gzip -cd $DB_BACKUP | docker exec -i docker_db_1 psql -U $POSTGRESQL_USER $POSTGRESQL_DBNAME
rc=$?
echo "restore DB tables, rc=$rc" >> $DB_LOG

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

# check
echo "# check" >> $DB_LOG
eval $PRINT_LOG
backup_rows=(`grep -n "^ レコード数" $DB_BACKUP_LOG | cut -d ':' -f 1`)
restore_rows=(`grep -n "^ レコード数" $DB_LOG | cut -d ':' -f 1`)
tables=("localitycode" "opendatamaps")
for i in 0 1; do
    backup_count=`tail -n +$((${backup_rows[$i]} + 2)) $DB_BACKUP_LOG | head -1`
    restore_count=`tail -n +$((${restore_rows[$i]} + 2)) $DB_LOG | head -1`
    if [ "$backup_count" != "$restore_count" ]; then
        echo "ERROR: バックアップログのレコード数と一致しません。${tables[$i]}" >> $DB_LOG
        echo "       ($backup_count != $restore_count)" >> $DB_LOG
        rc=21
    fi
    echo "  ${tables[$i]}: $backup_count = $restore_count" >> $DB_LOG
done
echo "check OK" >> $DB_LOG

if [ "$rc" == "0" ]; then
    mv "$DB_BACKUP" "${DB_BACKUP}.OK"
fi

echo "$(date '+%Y/%m/%d %H:%M:%S') db_backup.sh ended, rc=$rc" >> $DB_LOG
tail -n +$LOG_L $DB_LOG

exit $rc

