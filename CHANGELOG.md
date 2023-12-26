# Change Log

## 0.3.5 (To be released)

### Added

- New Characters:
  - Tartaglia
- New Cards:
  - Equipment Cards:
    - Talent Cards:
      - Abyssal Mayhem Hydrospout
  - Support Cards:
    - Liu Su
    - Rana
    - Setaria

### Updated

- Adjusted encoding of PlayerState to support new card in game version 4.3
- Version 4.3 balance patch applied
- Improved swap signal handling

## 0.3.4 (3 Dec 2023)

### Added

- Subclasses of `Deck` now supports conversion to and from json by calling
  `.to_json()` and `.from_json()`.
- Enables seeding when stepping `GameState`
- Implements customizable encoding for any `GameState`
- Smart dice selection that takes characters into account
- Implements `LinearEnv`, a gym-like environment for RL
- Implements `PlayerAction` encoding and decoding
- Implements `MutableDeck`, `FrozenDeck` encoding and decoding
- New Cards:
  - Event Card:
    - Fresh Wind of Freedom
    - When the Crane Returned

### Updated

- All the implemented cards and characters are now up-to-date with game version
  4.2.
- Perspective view of `GameState` now hides the dice of the opponent.
  (The only things left to hide are some certain statuses and effects)

### Fixed

- AbstractDice.cost_less_elem() has faulty behaviour when only ANY can be reduced.
- Hand card limit set in game mode was not enforced throughout the game.

## 0.3.3 (5 Nov 2023)

### Added

`dgisim` includes enum `ActionType` for action choosing.

- New Characters:
  - Dehya
  - Hu Tao
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Sanguine Rouge
      - Stalwart and True

## 0.3.2 (24 Oct 2023)

Removes preceding `v` in version name to be like `0.3.2`.

### Added

- New Characters:
  - Albedo
  - Collei
  - Fatui Pyro Agent
  - Fischl
  - Ganyu
  - Jadeplume Terrorshroom
  - Jean
  - Maguu Kenki
  - Ningguang
  - Qiqi
  - Sangonomiya Kokomi
  - Yoimiya
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Descent of Divinity
      - Floral Sidewinder
      - Lands of Dandelion
      - Naganohara Meteor Swarm
      - Paid in Full
      - Proliferating Spores
      - Rite of Resurrection
      - Stellar Predator
      - Strategic Reserve
      - Tamakushi Casket
      - Transcendent Automaton
      - Undivided Heart
    - Weapon Card:
      - A Thousand Floating Dreams
      - Amos' Bow
      - Aquila Favonia
      - Fruit of Fulfillment
      - King's Squire
      - Lithic Spear
      - The Bell
      - Vortex Vanquisher
      - Wolf's Gravestone
    - Artifact Card:
      - General's Ancient Helm
      - Instructor's Cap
      - Tenacity of the Millelith
  - Support Card:
    - Companion Card:
      - Chang the Ninth
      - Liben
      - Paimon
    - Item Card:
      - NRE
      - Parametric Transformer
    - Location Card:
      - Liyue Harbor Wharf
      - Sumeru City
      - Tenshukaku
  - Event Card:
    - Send Off
    - Tandoori Roast Chicken
    - The Bestest Travel Companion!
    - Where Is the Unseen Razor?

## v0.3.1 (28 Aug 2023)

### Added

- New Characters:
  - Bennett
  - Nahida
  - Noelle
  - Shenhe
  - Venti
  - Yae Miko
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Embrace of Winds
      - Grand Expectation
      - I Got Your Back
      - Mystical Abandon
      - The Seed of Stored Knowledge
      - The Shrine's Sacred Shade
    - Weapon Card:
      - Sacrificial Bow
      - Sacrificial Fragments
      - Sacrificial Greatsword
      - Sacrificial Sword
  - Event Card:
    - Elemental Resonance: Enduring Rock
    - Elemental Resonance: Fervent Flames
    - Elemental Resonance: High Voltage
    - Elemental Resonance: Impetuous Winds
    - Elemental Resonance: Shattering Ice
    - Elemental Resonance: Soothing Water
    - Elemental Resonance: Sprawling Greenery
    - Elemental Resonance: Woven Flames
    - Elemental Resonance: Woven Ice
    - Elemental Resonance: Woven Stone
    - Elemental Resonance: Woven Thunder
    - Elemental Resonance: Woven Waters
    - Elemental Resonance: Woven Weeds
    - Elemental Resonance: Woven Winds
    - Wind and Freedom

## v0.3.dev0 (6 Aug 2023)

### Added

- **Deck** related classes with card validity checking
- New Characters:
  - Electro Hypostasis
  - Mona
  - Xingqiu
- New Cards:
  - Talent Equipment Card:
    - Prophecy of Submersion
    - The Scent Remained
  - Artifact Card:
    - Gambler's Earrings
  - Location Card:
    - Knights of Favonius Library
    - Vanarana
  - Event Card:
    - I Haven't Lost Yet!
    - Food Card:
      - Teyvat Fried Egg
    - Talent Card:
      - Absorbing Prism

## v0.2.dev3 (27 Jul 2023)

### Added

At least one character of each element is now implemented

- New Characters:
  - Arataki Itto
  - Kaedehara Kazuha
  - Klee
  - Tighnari
- New Cards:
  - Charcter Talenet Card:
    - Arataki Ichiban
    - Keen Sight
    - Poetics of Fuubutsu
    - Pounding Surprise
  - Weapon Card:
    - Magic Guide
    - Raven Bow
    - Traveler's Handy Sword
    - White Iron Greatsword
    - White Tassel
  - Event Card:
    - Calxs Arts
    - Quick Knit

### Updated

- minor API change

## v0.2.dev2 (9 Jul 2023)

### Updated

- minor API change

## v0.2.dev1 (9 Jul 2023)

### Added

- methods to quick-create GameState / PlayerState / Characters
- includes some container classes in root dgisim
- unifies PS1 format

## v0.2.dev0 (9 Jul 2023)

### Added

- Adds link to documentation

### Updated

- Refines API
- CLI has full control of the player

## v0.1.dev0 (3 Jul 2023)

### Added

- Gives user the access to entire repo's src modules
