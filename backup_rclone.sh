#!/bin/bash

set -eu -o pipefail

LOCKFILE="/tmp/backup_rclone.lock"

# Use flock to ensure only one instance runs at a time
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Backup already running"; exit 1; }

# Define source and destination paths
SRC_DIR="$HOME/git/deuteron"
DEST_ONEDRIVE="onedrive-utk:backup/deuteron"

# Log file
LOG_FILE="$HOME/.local/logs/rclone_backup.log"

# Create log directory if not exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run rclone sync for Dropbox, appending output to log
{
    echo "==== Backup started at $(date) ===="

    # Sync data and logs to OneDrive UTK 
    rclone sync "$SRC_DIR/data" "$DEST_ONEDRIVE/data" --progress --log-file="$LOG_FILE" --log-level INFO
    rclone sync "$SRC_DIR/logs" "$DEST_ONEDRIVE/logs" --progress --log-file="$LOG_FILE" --log-level INFO

    echo "==== Backup completed at $(date) ===="
} >> "$LOG_FILE" 2>&1
