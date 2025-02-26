#!/bin/bash
# Move to current directory
cd "$(dirname "$0")" || exit 1

TIMESTAMP=$(date "+%Y-%m-%d_%H:%M:%S")

# Create logs directory in the same directory as the script
mkdir -p ./logs
LOG_FILE="./logs/$TIMESTAMP.log"

python bot.py >> "$LOG_FILE" 2>&1

# Echo a string to the file
echo "Script finished at $(date)" >> "$LOG_FILE" 