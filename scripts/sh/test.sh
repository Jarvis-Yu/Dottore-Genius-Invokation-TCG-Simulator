#!/bin/bash
export RNG_PLAYS=5
echo -ne "#################### Unittest ####################\n" && \
./venv/bin/coverage run -m unittest && \
echo -ne "\n#################### Mypy ####################\n" && \
./venv/bin/mypy src/ --check-untyped-defs && \
echo -ne "\n#################### Coverage ####################\n" && \
./venv/bin/coverage report