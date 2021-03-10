#!/bin/bash -eu
apt-get install -y scrot
python3.6 -m pip uninstall -y QWeb || true