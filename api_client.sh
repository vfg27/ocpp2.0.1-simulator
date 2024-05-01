#!/bin/sh

"$(dirname "$0")/venv/bin/python" "$(dirname "$0")/charging/api_client.py" "$@"
