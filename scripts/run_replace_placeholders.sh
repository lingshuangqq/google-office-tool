#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <DOC_ID> <PLACEHOLDER> <MARKDOWN_FILE_PATH>"
  exit 1
fi
DOC_ID=$1
PLACEHOLDER=$2
MARKDOWN_FILE=$3
python3 "$(dirname "$0")/../src/client.py" docs replace $DOC_ID $PLACEHOLDER $MARKDOWN_FILE
