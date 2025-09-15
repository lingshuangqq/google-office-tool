#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: $0 <DOC_ID>"
  exit 1
fi
DOC_ID=$1
python3 "$(dirname "$0")/../src/client.py" docs clear $DOC_ID
