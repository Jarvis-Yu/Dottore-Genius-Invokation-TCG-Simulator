#!/bin/bash
if [ ! -d "venv" ]; then
  python -m venv venv
fi
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:`pwd`/dgisim"
