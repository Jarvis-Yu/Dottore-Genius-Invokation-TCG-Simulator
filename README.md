# Dottore Genius Invokation TCG Simulator

[![PyPI Version](https://img.shields.io/pypi/v/dgisim.svg)](https://pypi.org/project/dgisim/)
[![Documentation Status](https://readthedocs.org/projects/dottore-genius-invokation-tcg-simulator/badge/?version=latest)](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/latest/?badge=latest)
![Python 3.10](https://img.shields.io/badge/python->=3.10-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/badge.svg?branch=master)](https://coveralls.io/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator?branch=master)
[![license](https://img.shields.io/github/license/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator)](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/LICENSE)

A Genshin Impact Genius Invokation TCG simulator intended to be used for Reinforcement Learning.

- [**Documentation**](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/)
- [**Source code**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator)
- [**Contributing**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/dev_docs/dev_readme.md)
- [**Game design**](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/design-n-philosophy.html)
- [**Bug reports**](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/issues)
- [**Discord server**](https://discord.gg/arammB6BEY)

This package aims to help programmers code things based on Genius Invokation
TCG with ease. e.g. AI, desktop application, website...

The simulator is modeled as a finite state machine, where all game states are immutable.
Optimizations are done to make sure immutability doesn't impact performance.

Basic rules of Genius Invokation TCG can be found on [Fandom](https://genshin-impact.fandom.com/wiki/Genius_Invokation_TCG).

## Installation

Please make sure your Python version `>= 3.10` before installing.

```
pip install dgisim
```

## RL Environment Usage Example

```python
from dgisim import LinearEnv

env = LinearEnv()
rl_net = ...  # your RL network

for episode range(100):
    env.reset()
    game_state, encoded_state, reward, turn, done = env.view()

    while not done:
        ...  # do the training on the encoded_state
        game_state, encoded_state, reward, turn, done = env.step(action)
```

For more details please check the [documentation](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/tutorials/rl.html).

## Try the Simulator in Browser

- Website: [https://jarvis-yu.github.io/Dottore-Genius-Invokation-TCG-PWA/](https://jarvis-yu.github.io/Dottore-Genius-Invokation-TCG-PWA/)
- Repo: [https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-PWA](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-PWA)

## Try the Simulator in CLI

### Run Locally

Once installed, you may start by trying the CLI to play the game first.

You might want to run a simple python program like this:

```py
from dgisim import CLISession

session = CLISession()
session.run()
```

### Run Remotely

You may try the CLI online on [Google Colab](https://colab.research.google.com/drive/1h6ckw4LQ2jMEnZAs9QQo6tHjCwWnR8KD?usp=sharing)

### CLI Simple Usages

See CLI's [tutorial](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/tutorials/cli.html)
for showcase and explanations of the CLI.

## Features

The package allows:

- Customization of player agents
- Customization of characters
- Customization of cards
- Customization of game modes

This simulator is modeled as a finite state machine, which means any intermediate state can be
standalone and be used to proceed to other states.

The `GameState` class represents some game state in the state machine. It uses passed in
`Phase` object to determine how to transform to another state, which means the game flow is
highly customizable. (Default Mode and some Heated Battle Modes are implemented already)

Everything in the `GameState` object are immutable, so traversing game history
and exploring different branches of possibilities in the future are not error-prone.
stable simulator did optimizations for immutability.
The unchanged data are shared among neighbouring game states.

`GameState` implements `__eq__` and `__hash__`, enabling you to use any game state as a key in a
dictionary, and discover game states on different 'game branches' being actually the same.

An `ActionGenerator` can be returned by any valid `GameState` to help
generate valid player actions.

## Development Milestones

Currently a full game can be played with any combination of the characters and cards implemented.

- [x] Implement all game phases (Action Phase, End Phase...)
- [ ] Implement all cards (99/217 implemented)
      ([latest-details](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/latest/card/available-cards.html))
      ([stable-details](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/card/available-cards.html))
- [ ] Implement all characters with their talent cards (30/60 implemented)
      ([latest-details](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/latest/character/available-chars.html))
      ([stable-details](https://dottore-genius-invokation-tcg-simulator.readthedocs.io/en/stable/character/available-chars.html))
- [x] Implement all reactions, death handling, revival handling etc.
- [x] Implement all game logics to support the implemented cards and characters
- [x] Implement interactive CLI for better debugging experience
- [x] Ensure 99% unittest coverage checking behaviour of characters and cards
- [x] Implement lazy player agent for minimal testing purposes
- [x] Implement random player agent for testing purposes
- [x] Implement player action validity checker
- [x] Implement player action choices provider

## Future Plans

I have the plan to implement a simple cross-platform GUI interface for the simulator.
But that will be in a separate repo.

Once this project is done, I'll be reading relative papers and develop an AI for this game.
The AI is supposed to be used for learning strategies and making decks,
but not against another player directly.
