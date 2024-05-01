#!/bin/sh

"$(dirname "$0")/venv/bin/python" "$(dirname "$0")/charging/server.py" "$@"
