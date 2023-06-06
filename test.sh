#!/bin/bash
./venv/bin/python -m unittest
./venv/bin/mypy dgisim/ --check-untyped-defs