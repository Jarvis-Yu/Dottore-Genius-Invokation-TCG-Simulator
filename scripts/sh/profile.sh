#!/bin/bash
./venv/bin/python -O -m src.profiles.profile_random_game && \
./venv/bin/python -m snakeviz game_play.prof
