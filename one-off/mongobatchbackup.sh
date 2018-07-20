#!/bin/bash
MONGODB_HOST='127.0.0.1:27017'
S3_BUCKET='s3/buckets/wehome-airbnb-backup'

# Get the directory the script is being run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR

# Store the current date in YYYY-mm-DD-HHMMSS
if [ -z "$1" ]; then
  DATE=$(date --date="2 days ago" -u "+%F-%H%M%S")
  DATE_=$(date --date="2 days ago" -u "+%F")
else
  DATE=$1
  DATE_=$DATE
fi
echo $DATE
echo $DATE_

FILE_NAME="backup-airbnb-$DATE"
ARCHIVE_NAME="$FILE_NAME.tar.gz"

# Lock the database
# Note there is a bug in mongo 2.2.0 where you must touch all the databases before you run mongodump
mongo  --host "$MONGODB_HOST"  --eval "var databaseNames = db.getMongo().getDBNames(); for (var i in databaseNames) { printjson(db.getSiblingDB(databaseNames[i]).getCollectionNames()) }; printjson(db.fsyncLock());"

# Dump the database
COLLECTION="Airbnb-"$DATE_
mongodump  --host "$MONGODB_HOST" --db "Airbnb" --collection $COLLECTION  --out $DIR/backup/$FILE_NAME

# Unlock the database
mongo --host "$MONGODB_HOST"  --eval "printjson(db.fsyncUnlock());"

# Tar Gzip the file
tar -C $DIR/backup/ -zcvf $DIR/backup/$ARCHIVE_NAME $FILE_NAME/

# Remove the backup directory
rm -r $DIR/backup/$FILE_NAME

# Send the file to the backup drive or S3
aws s3 cp $DIR/backup/$ARCHIVE_NAME s3://$S3_BUCKET/$ARCHIVE_NAME
