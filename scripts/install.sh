#!/bin/sh

sudo python3 -m venv "$(dirname "$0")"/../venv
sudo "$(dirname "$0")"/../venv/bin/pip install -r "$(dirname "$0")"/../requirements.txt
