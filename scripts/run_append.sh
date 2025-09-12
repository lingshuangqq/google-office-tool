#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <DOC_ID> <TEXT_TO_APPEND>"
  exit 1
fi
DOC_ID=$1
TEXT_TO_APPEND=$2
python3 "$(dirname "$0")/../src/client.py" docs append $DOC_ID "$TEXT_TO_APPEND"