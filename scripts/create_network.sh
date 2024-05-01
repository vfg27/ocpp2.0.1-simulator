#!/bin/sh

echo "===== CLEANING ====="
sudo python3 -m ipmininet.clean

echo "===== CREATING ====="
sudo python3 "$(dirname "$0")./network/create_network.py"
