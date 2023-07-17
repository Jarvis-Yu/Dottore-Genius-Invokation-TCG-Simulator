# Dottore Genius Invokation TCG Simulator

![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/badge.svg?branch=master)](https://coveralls.io/github/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator?branch=master)

A Genshin Impact Genius Invokation TCG simulator intended to be used for AI training (for now).

The simulator is modeled as a finite state machine, where all game states are immutable.

Basic rules of Genius Invokation TCG can be found [here](https://genshin-impact.fandom.com/wiki/Genius_Invokation_TCG).

## Installation

Make sure your Python version `>= 3.10`.

```
pip install dgisim
```

Note that this is a developing project and the final API to users is not set in stone.
So you may play with it, but using it in production is not recommended at the current stage.

## [Documentation](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/wiki)

## Simple Guide

Once installed, you may have a try with the CLI to play the simulator in command line.

You might want to run a simple python program like this:

```py
from dgisim import CLISession

session = CLISession()
session.run()
```

Or try it online on [Google Colab](https://colab.research.google.com/drive/1h6ckw4LQ2jMEnZAs9QQo6tHjCwWnR8KD?usp=sharing)

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

## [State Machine Design](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/state_machine_design.md)

## Development Milestones

- [x] Set up the framework for maintaining game states
- [x] Implement game phase of Card Selection (card selection at the start of the game)
- [x] Implement game phase of Starting Hand Select Phase (select active character)
- [x] Implement game phase of Roll (Dice) Phase (roll dices between rounds)
- [x] Implement game phase of Action Phase (players beat each other)
  - [ ] Implement all cards (24/184 implemented)
    - [x] Calxs Arts,
          Changing Shifts,
          ColdBlooded Strike,
          Jueyun Guoba,
          Keen Sight,
          Leave It to Me!,
          Lightning Stiletto,
          Lotus Flower Crisp,
          Magic Guide,
          Minty Meat Rolls,
          Mondstadt Hash Brown,
          Mushroom Pizza,
          Nothern Smoked Chicken,
          Pounding Surprise,
          Quick Knit,
          RavenBow,
          Starsigns,
          Streaming Surge,
          Sweet Madame,
          Thundering Penance,
          TravelersHandySword,
          White Iron Greatsword,
          White Tassel,
          Xudong,
  - [ ] Implement all characters with their talent cards (5/48 implemented)
    - [x] Kaeya,
          Keqing,
          Klee,
          Rhodeia of Loch,
          Tighnari,
  - [x] Implement all reactions
- [x] Implement game phase of End Phase (summons and some support card or statuses take action)
- [x] Implement game phase of Game End Phase (one player wins or draw)
- [x] Implement CLI for better debugging experience
- [x] Implement interactive active CLI that accepts user input as action
- [x] Implement lazy player agent for minimal testing purposes
- [x] Implement random player agent for testing purposes
- [x] Implement player action validity checker
- [x] Implement player action choices provider

> Just in case you don't know, **_WIP_** means "work in progress".

## Future Plans

I have the plan to implement a simple cross-platform GUI interface for the simulator. But that will
be in a separate repo.

Once this project is done, I'll be reading relative papers and develop an AI for this game. The AI
is supposed to be used for learning strategies and making decks, but not against another player
directly.

## Wants To Contribute?

Please read [this](https://github.com/Jarvis-Yu/Dottore-Genius-Invokation-TCG-Simulator/blob/master/docs/dev_readme.md).
