# Dottore Genius Invokation TCG Simulator

[![Coverage Status](https://coveralls.io/repos/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/badge.svg?branch=master)](https://coveralls.io/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator?branch=master)

A Genshin Impact Genius Invokation TCG simulator intended to be used for AI training (for now).

The simulator is modeled as a finite state machine, where all game states are immutable.

## Install

Make sure your Python version `>= 3.10.11`.

```shell
pip install dgisim
```

Note that this is a developing project and the final API to users is not set in stone.
So you may play with it, but using it in production is not recommended at the current stage.

## Simple Guide

Once installed, you may have a try with the CLI to play the simulator in command line.

You might want to run a simple python program like this:

```py
from dgisim.cli import CLISession

session = CLISession()
session.run()
```

See CLI's [README](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/cli_readme.md)
for showcase and explanations of the CLI.

## Features of This Simulator

First of all, it is modeled as a finite state machine, which means any intermediate state can be
standalone and be used to proceed to other states.

Also, the `GameState` class, which represents some game state in the state machine, uses passed in
`Phase` object to determine how to transform to another state, which means the game flow is
highly customizable.

Everything in the `GameState` object are immutable, so traversing game history and exploring different
branches of possibilities in the future are not error-prone. Do not worry about memory efficiency,
everything is immutable, so only the modified part between neighbouring game states are added to the
memory.

`GameState` implements `__eq__` and `__hash__`, enabling you to use any game state as a key in a
dictionary, and discover game states on different 'game branches' being actually the same.

## Development Milestones

- [x] Set up the framework for maintaining game states
- [x] Implement game phase of Card Selection (card selection at the start of the game)
- [x] Implement game phase of Starting Hand Select Phase (select active character)
- [x] Implement game phase of Roll (Dice) Phase (roll dices between rounds)
- [x] Implement game phase of Action Phase (players beat each other)
  - [ ] Implement all cards (15/184 implemented)
    - [x] Changing Shifts,
          ColdBlooded Strike,
          Jueyun Guoba,
          Leave It to Me!,
          Lightning Stiletto,
          Lotus Flower Crisp,
          Minty Meat Rolls,
          Mondstadt Hash Brown,
          Mushroom Pizza,
          Nothern Smoked Chicken,
          Starsigns,
          Streaming Surge,
          Sweet Madame,
          Thundering Penance,
          Xudong,
  - [ ] Implement all characters with their talent cards (3/48 implemented)
    - [x] Kaeya,
          Keqing,
          Rhodeia of Loch,
  - [x] Implement all reactions
- [x] Implement game phase of End Phase (summons and some support card or statuses take action)
- [x] Implement game phase of Game End Phase (one player wins or draw)
- [x] Implement CLI for better debugging experience
- [x] Implement interactive active CLI that accepts user input as action
- [x] Implement lazy player agent for minimal testing purposes
- [x] Implement random player agent for testing purposes
- [x] Implement player action validity checker
- [ ] Implement player action choices provider
  - [x] all action phase choices provider
  - [x] all end phase choices provider
  - [ ] Other choices provider (trivial for now)
- [ ] Implement greedy player agent for testing purposes

> Just in case you don't know, **_WIP_** means "work in progress".

## Future Plans

The fully developed project will be published to PyPI (beta versions will be available once all that
are left is adding more characters and cards)

I have the plan to implement a simple cross-platform GUI interface for the simulator. But that will
be in a separate repo.

Once this project is done, I'll be reading relative papers and develop an AI for this game. The AI
is supposed to be used for learning strategies and making decks, but not against another player
directly.

## Interested in the Project?

Please read this [README](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/dev_readme.md).
