#!/bin/bash
RED='\033[0;31m'
NC='\033[0m'
printf "${RED}UPLOADING TO PYPI NOT TESTPYPI!${NC}\n"
tree dist/
printf "${RED}ENTER TO PROCEED: ${NC}" && read
./venv/bin/python -m twine upload dist/*