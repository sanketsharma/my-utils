#!/bin/bash

LOCKFILE="/tmp/backup_rclone.lock"

# Use flock to ensure only one instance runs at a time
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Backup already running"; exit 1; }

# Define source and destination paths
SRC_DIR="$HOME/git/deuteron"
DEST_GDRIVE="gdrive:backup/deuteron"
DEST_DROPBOX="dropbox:backup/deuteron"

# Log file
LOG_FILE="$HOME/.local/logs/rclone_backup.log"

# Create log directory if not exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run rclone sync for Google Drive and Dropbox, appending output to log
{
    echo "==== Backup started at $(date) ===="

    # Sync data and logs to Google Drive
    rclone sync "$SRC_DIR/data" "$DEST_GDRIVE/data" --progress --log-file="$LOG_FILE" --log-level INFO
    rclone sync "$SRC_DIR/logs" "$DEST_GDRIVE/logs" --progress --log-file="$LOG_FILE" --log-level INFO

    # Sync data and logs to Dropbox
    rclone sync "$SRC_DIR/data" "$DEST_DROPBOX/data" --progress --log-file="$LOG_FILE" --log-level INFO
    rclone sync "$SRC_DIR/logs" "$DEST_DROPBOX/logs" --progress --log-file="$LOG_FILE" --log-level INFO

    echo "==== Backup completed at $(date) ===="
} >> "$LOG_FILE" 2>&1
