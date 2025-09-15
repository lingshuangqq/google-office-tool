#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: $0 <MARKDOWN_FILE_PATH> [DRIVE_FOLDER_ID] [TEMPLATE_ID] [TITLE]"
  exit 1
fi
MARKDOWN_FILE=$1
ARGS=()
if [ ! -z "$2" ]; then
  ARGS+=(--folder_id "$2")
fi
if [ ! -z "$3" ]; then
  ARGS+=(--template_id "$3")
fi
if [ ! -z "$4" ]; then
  ARGS+=(--title "$4")
fi
python3 "$(dirname "$0")/../src/client.py" slides create "$MARKDOWN_FILE" "${ARGS[@]}"
