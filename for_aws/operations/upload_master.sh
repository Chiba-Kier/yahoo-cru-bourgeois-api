#!/bin/bash
# Usage: ./upload_master.sh <S3_BUCKET_NAME>

BUCKET_NAME=$1

if [ -z "$BUCKET_NAME" ]; then
    echo "Usage: ./upload_master.sh <S3_BUCKET_NAME>"
    exit 1
fi

# Get absolute path of data directory relative to script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../../for_local/data"

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory not found at $DATA_DIR"
    exit 1
fi

echo "Syncing master data to s3://$BUCKET_NAME/master/ ..."
aws s3 sync "$DATA_DIR" "s3://$BUCKET_NAME/master/" --exclude "*" --include "*.csv"

echo "Sync completed successfully."
