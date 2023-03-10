# Dottore Genius Invokation TCG Simulator

A Genshin Impact Genius Invokation TCG simulator intended to be used for AI training (for now).

The simulator is modeled as a finite state machine, where all game states are immutable.

- [Dottore Genius Invokation TCG Simulator](#dottore-genius-invokation-tcg-simulator)
  - [Development Milestones](#development-milestones)
  - [Currently Working On](#currently-working-on)
  - [Future Plans](#future-plans)
  - [QA](#qa)

## Development Milestones

The aim of my first stage is to make the games runs with characters Oceanid, Kaeya and Keqing,
with limited action cards and all omni dices.

- [x] Set up the framework for maintaining game states
- [x] Implement game phase of Card Selection (card selection at the start of the game)
  - [x] Basiclly work and can continue to next phase of the game
  - [x] Can work with real cards
  - [ ] ~~Allow both players to act simultaneously instead of in turns~~ (trivial for AI training)
- [x] Implement game phase of Starting Hand Select Phase (select active character)
- [ ] Implement game phase of Roll (Dice) Phase (roll dices between rounds)
  - [x] Can provide all omni dices
  - [x] Can proceed to next phase
- [ ] Implement game phase of Action Phase (players beat each other)
  - [x] Allow players to end action phase right away
  - [ ] Implement the pipeline for buff handling
  - [ ] Allow players to normal attack
  - [ ] Allow players to cast skills
  - [ ] Allow players to cast elemental burst
  - [x] Can proceed to next phase
- [ ] Implement game phase of End Phase (summons and some support card or buffs take action)
  - [x] Can pull cards by the end
  - [x] Can proceed to next phase
- [x] Implement game phase of Game End Phase (one player wins or draw)
- [x] Implement lazy player agent for minimal testing purposes
- [ ] Implement random player agent for testing purposes
- [ ] Implement greedy player agent for testing purposes

The third stage is to implement real dices system.

The second stage of development will be focusing on including all action cards.

The final stage is to include more characters and eventually all.

## Currently Working On

Designing action phase as a state machine (and a mix of flow chart).

The design doc can be read [here](docs/state_machine_design.md).

## Future Plans

The fully developed project will be published to PyPI (beta versions will be available once all that
are left is adding more characters)

Once this project is done, I'll be reading relative papers and develop an AI for this game. The AI
is supposed to be used for learning strategies and making decks, but not against another player
directly.

## QA

Why are you implementing the simulator that is already under development on github?

- It entertains me to design and code.

So you don't want any teammates?

- Well, collaborators are welcomed. If you have the intention to join, please contact me.

How to contact you?

- I assume you can find my email somewhere, if not, raise an issue on this project so I'll be
  notified.
