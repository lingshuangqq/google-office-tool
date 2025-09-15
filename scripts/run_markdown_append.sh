#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <DOC_ID> <MARKDOWN_FILE_PATH>"
  exit 1
fi
DOC_ID=$1
MARKDOWN_FILE=$2
python3 "$(dirname "$0")/../src/client.py" docs append $DOC_ID --file $MARKDOWN_FILE