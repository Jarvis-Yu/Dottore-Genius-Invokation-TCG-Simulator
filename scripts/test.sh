#!/bin/bash
#./venv/bin/python -m unittest
echo -ne "#################### Unittest ####################\n" && \
./venv/bin/coverage run -m unittest && \
echo -ne "\n#################### Mypy ####################\n" && \
./venv/bin/mypy dgisim/ --check-untyped-defs && \
echo -ne "\n#################### Coverage ####################\n" && \
./venv/bin/coverage report