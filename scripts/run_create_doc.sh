#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <TITLE> <MARKDOWN_FILE_PATH> [FOLDER_ID]"
  exit 1
fi
TITLE=$1
MARKDOWN_FILE=$2
FOLDER_ID_ARG=""
if [ ! -z "$3" ]; then
  FOLDER_ID_ARG="--folder_id $3"
fi
python3 "$(dirname "$0")/../src/client.py" docs write "$MARKDOWN_FILE" --title "$TITLE" $FOLDER_ID_ARG
