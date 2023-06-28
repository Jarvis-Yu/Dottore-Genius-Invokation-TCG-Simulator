#!/bin/bash
export PYTHONPATH=$PYTHONPATH:`pwd`
./venv/bin/python -O dgisim/profiles/profile_random_game.py
./venv/bin/python -m snakeviz game_play.prof