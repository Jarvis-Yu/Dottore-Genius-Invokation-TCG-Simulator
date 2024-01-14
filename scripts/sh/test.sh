#!/bin/bash
export RNG_PLAYS=5
export ENCODING_RUNS=2
export SHOW_PROGRESS=1
echo -ne "#################### Unittest ####################\n" && \
./venv/bin/coverage run -m unittest discover src/tests/ && \
echo -ne "\n#################### Mypy ####################\n" && \
./venv/bin/mypy src/ --check-untyped-defs && \
echo -ne "\n#################### Coverage ####################\n" && \
./venv/bin/coverage report && \
./venv/bin/coverage html