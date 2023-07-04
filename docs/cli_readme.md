# CLI Introduction

- [CLI Introduction](#cli-introduction)
  - [Show Case on How to Use the CLI](#show-case-on-how-to-use-the-cli)

## Show Case on How to Use the CLI

After setting up the environment following the instructions in the main [README](../README.md),
you may run `./scripts/sh/cli.sh` under the project directory to start a CLI session.

Below shows what you are likely to see.

(Just note that I may make comments starting with `//` in the code blocks,
they are just to explain certain parts,
but not actually printed when you use the CLI)

``` terminal
$ ./scripts/sh/cli.sh    // though it is run via a script here, but it is the same
                      // if you pip-installed the module and run it
==================================================
Welcome to the Dottore Genius Invokation TCG Simulator CLI ver.
This is currently just a basic version for debugging only.
==================================================
Commands:
a    - to forward to an autostep
n    - to forward to next step
ba   - to previous autostep
bn   - to previous step
h    - to get help
q    - to quit this session
     - enter nothing to repeat last step
rst  - to reset game session (and choose next game mode)

Note: any invalid commands are ignored

Definitions:
- autostep - jumps to the next game-state where player interaction is required
- step - jumps to the next game-state
==================================================
Please choose the cli mode:
Choices are:
@0: PVP  |||  @1: PVE  |||  @2: EVE

Please choose id (0-2): @    // this is where you make your first input
```

So as shown above, you need to input a number from 0 to 2,
to save some time and experience all features.
Let's say we choose 1 for PVE this time.

``` terminal
Please choose the cli mode:
Choices are:
@0: PVP  |||  @1: PVE  |||  @2: EVE

Please choose id (0-2): @1    // last input is '1'

==================================================
<Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Passive Wait Phase>   | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <Keqing>                    |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
<Deck Cards>                  | <Deck Cards>                  |
  <SweetMadame: 2>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 2>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
  <Xudong: 2>                 |   <Xudong: 2>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 2>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 2>         |   <ChangingShifts: 2>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 2>         |
  <JueyunGuoba: 2>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 2>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 2>      |   <ThunderingPenance: 2>      |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================

:>    // next input goes here
```

So the initial game state is printed,
and hopefully you remember what commands you have,
lemme give you a quick reminder.

``` terminal
Commands:
a    - to forward to an autostep
n    - to forward to next step
ba   - to previous autostep
bn   - to previous step
h    - to get help
q    - to quit this session
     - enter nothing to repeat last step
rst  - to reset game session (and choose next game mode)

Note: any invalid commands are ignored

Definitions:
- autostep - jumps to the next game-state where player interaction is required
- step - jumps to the next game-state
```

Most of the time `a` is the most useful command to use,
as it helps skip tedious status handling intermediate game states when player make a move.
But `h` can come handy when you forgot which commands you can use.
(giving invalid commands 3 times in a row automatically triggers help prompting)

Alright, let's give command `a` to the CLI.

``` terminal
:> a    // last input is 'a'
<Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Action Phase>         |
<Card Redraw Chances: 1>      | <Card Redraw Chances: 1>      |
<Characters>                  | <Characters>                  |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <Keqing>                    |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
  <LotusFlowerCrisp: 1>       |   <LotusFlowerCrisp: 1>       |
  <Xudong: 1>                 |   <MintyMeatRolls: 1>         |
  <NorthernSmokedChicken: 1>  |   <Starsigns: 1>              |
  <SweetMadame: 1>            |   <ChangingShifts: 1>         |
  <ThunderingPenance: 1>      |   <ColdBloodedStrike: 1>      |
<Deck Cards>                  | <Deck Cards>                  |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 1>  |   <NorthernSmokedChicken: 2>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
  <Xudong: 1>                 |   <Xudong: 2>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 1>       |   <LotusFlowerCrisp: 1>       |
  <ChangingShifts: 2>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 2>         |
  <JueyunGuoba: 2>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 1>      |
  <MondstadtHashBrown: 2>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 1>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player1 Action: CardSelectAction[<LotusFlowerCrisp>: 1; <NorthernSmokedChicken>: 1; <SweetMadame>: 1; ]

:> 
```

You may have noticed this by the end of the last code-block.

```
#### Player1 Action: CardSelectAction[<LotusFlowerCrisp>: 1; <NorthernSmokedChicken>: 1; <SweetMadame>: 1; ]
```

It is the automatic message indicating what the player's action is in this game state.

Some people may have questions here.
"Didn't I choose **PVE**, why the action is done automatically?"

Well, sorry about that,
the user-interaction for the initializing phases of the game are not done yet.
But trust me, you are free to choose what you want to do once you are in the ***action phase***,
which is the one players care the most right?

So for now, let's `auto-step` all the way to ***action phase***.

``` terminal
:>     // noticed there's no input here?
        // Actually I just entered nothing to repeat last command
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*RhodeiaOfLoch>            |   <RhodeiaOfLoch>             |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <*Keqing>                   |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 8>                   |   <OMNI: 8>                   |
<Hand Cards>                  | <Hand Cards>                  |
  <Xudong: 1>                 |   <LotusFlowerCrisp: 1>       |
  <MondstadtHashBrown: 1>     |   <ChangingShifts: 1>         |
  <Starsigns: 1>              |   <JueyunGuoba: 1>            |
  <LeaveItToMe: 1>            |   <Starsigns: 1>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 1>      |
<Deck Cards>                  | <Deck Cards>                  |
  <SweetMadame: 2>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 2>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
  <Xudong: 1>                 |   <Xudong: 2>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 2>         |
  <LeaveItToMe: 1>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 1>       |
  <ChangingShifts: 2>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 2>         |
  <JueyunGuoba: 2>            |   <JueyunGuoba: 1>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 1>              |   <Starsigns: 1>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 1>      |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @     // next input goes here
```

As usual, the latest game state is nicely printed,
and the prompt at the bottom tells you it's player1's turn.
(when in PVE mode, the user is player1)

Now you may choose the category of action that you want to do.

***Warning***: once you have entered you choice to CLI, you cannot redo what you've done.
Unless for some reason, you cannot use the entire category of action.
(e.g. if you choose `Skill` when your character is frozen
or you just don't have enough dices for any skill,
then your request is automatically judged as invalid and CLI will prompt you to make another choice)

(The redo thing is just not implemented currently as it has a low priority)

Anyways, as we have `Xudong` in our hands, let's play it.

``` terminal
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @0    // first input

Choices are:
@0: Xudong  |||  @1: Starsigns  |||  @2: LeaveItToMe

Please choose id (0-2): @0    // second input

#### Player1 Action: <Xudong, DiceOnlyInstruction:(dices=<OMNI>: 2
)>

:> 
```

(Note that you don't need to (a better way of saying currently you cannot) choose the dices
to pay for your action. It is automatically chosen for you. And as to the all `OMNI` dices thing,
other dices are supported, but to make sure you can play as you wish, I made game to only
give you `OMNI` dices.)

You may have noticed your action is accepted (seeing `#### ...`), hooray!

Wait, why am I not seeing what is happening next?
The reason is CLI asked for an action because it cannot proceed without one.
But you are the one who need to control if the game-state should *step* forward.

Remember your last command input? `a` that is. So enter nothing to proceed.

```
:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*RhodeiaOfLoch>            |   <RhodeiaOfLoch>             |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <*Keqing>                   |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
  <Xudong<1>: (1)>            | <Dices>                       |
<Dices>                       |   <OMNI: 8>                   |
  <OMNI: 6>                   | <Hand Cards>                  |
<Hand Cards>                  |   <LotusFlowerCrisp: 1>       |
  <LeaveItToMe: 1>            |   <ChangingShifts: 1>         |
  <MondstadtHashBrown: 1>     |   <JueyunGuoba: 1>            |
  <Starsigns: 1>              |   <Starsigns: 1>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 1>      |
<Deck Cards>                  | <Deck Cards>                  |
  <SweetMadame: 2>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 2>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
  <Xudong: 1>                 |   <Xudong: 2>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 2>         |
  <LeaveItToMe: 1>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 1>       |
  <ChangingShifts: 2>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 2>         |
  <JueyunGuoba: 2>            |   <JueyunGuoba: 1>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 1>              |   <Starsigns: 1>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 1>      |
<Publicly Used Cards>         | <Publicly Used Cards>         |
  <Xudong: 1>                 |                               |
---------------------------------------------------------------
<Effects>
===============================================================
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @
```

Playing `Xudong` isn't a combat action, so it is still your turn.

According to the `game state` printed above, my active character is Rhodeia (Oceanid).
Let's summon!

``` terminal
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @1

Choices are:
@0: NORMAL_ATTACK  |||  @1: ELEMENTAL_SKILL1  |||  @2: ELEMENTAL_SKILL2

Please choose id (0-2): @2

#### Player1 Action: <CharacterSkill.ELEMENTAL_SKILL2, DiceOnlyInstruction:(dices=<OMNI>: 5
)>

:> 
```

And enter nothing to proceed.

``` terminal
:>     // last input
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: Player1>             | <Player: *Player2>            |
<Phase: Passive Wait Phase>   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*RhodeiaOfLoch>            |   <RhodeiaOfLoch>             |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <*Keqing>                   |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
  <OceanicMimicSquirrel: 2>   | <Supports>                    |
  <OceanicMimicFrog: 2>       | <Dices>                       |
<Supports>                    |   <OMNI: 8>                   |
  <Xudong<1>: (1)>            | <Hand Cards>                  |
<Dices>                       |   <LotusFlowerCrisp: 1>       |
  <OMNI: 1>                   |   <ChangingShifts: 1>         |
<Hand Cards>                  |   <JueyunGuoba: 1>            |
  <LeaveItToMe: 1>            |   <Starsigns: 1>              |
  <MondstadtHashBrown: 1>     |   <ThunderingPenance: 1>      |
  <Starsigns: 1>              | <Deck Cards>                  |
  <ThunderingPenance: 1>      |   <SweetMadame: 2>            |
<Deck Cards>                  |   <NorthernSmokedChicken: 2>  |
  <SweetMadame: 2>            |   <MushroomPizza: 2>          |
  <NorthernSmokedChicken: 2>  |   <Xudong: 2>                 |
  <MushroomPizza: 2>          |   <MintyMeatRolls: 2>         |
  <Xudong: 1>                 |   <LeaveItToMe: 2>            |
  <MintyMeatRolls: 2>         |   <LotusFlowerCrisp: 1>       |
  <LeaveItToMe: 1>            |   <ChangingShifts: 1>         |
  <LotusFlowerCrisp: 2>       |   <StreamingSurge: 2>         |
  <ChangingShifts: 2>         |   <JueyunGuoba: 1>            |
  <StreamingSurge: 2>         |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 2>            |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>      |   <Starsigns: 1>              |
  <MondstadtHashBrown: 1>     |   <ThunderingPenance: 1>      |
  <Starsigns: 1>              | <Publicly Used Cards>         |
  <ThunderingPenance: 1>      |                               |
<Publicly Used Cards>         |                               |
  <Xudong: 1>                 |                               |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player2 Action: SwapAction:(char_id=1, instruction=DiceOnlyInstruction:(dices=<OMNI>: 1
))

:> 
```

The computer (random player) dicided to make a swap, alright. Enter to proceed to my turn.

``` terminal
:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*RhodeiaOfLoch>            |   <*RhodeiaOfLoch>            |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Keqing>                    |   <Keqing>                    |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
  <OceanicMimicSquirrel: 2>   | <Supports>                    |
  <OceanicMimicFrog: 2>       | <Dices>                       |
<Supports>                    |   <OMNI: 7>                   |
  <Xudong<1>: (1)>            | <Hand Cards>                  |
<Dices>                       |   <LotusFlowerCrisp: 1>       |
  <OMNI: 1>                   |   <ChangingShifts: 1>         |
<Hand Cards>                  |   <JueyunGuoba: 1>            |
  <LeaveItToMe: 1>            |   <Starsigns: 1>              |
  <MondstadtHashBrown: 1>     |   <ThunderingPenance: 1>      |
  <Starsigns: 1>              | <Deck Cards>                  |
  <ThunderingPenance: 1>      |   <SweetMadame: 2>            |
<Deck Cards>                  |   <NorthernSmokedChicken: 2>  |
  <SweetMadame: 2>            |   <MushroomPizza: 2>          |
  <NorthernSmokedChicken: 2>  |   <Xudong: 2>                 |
  <MushroomPizza: 2>          |   <MintyMeatRolls: 2>         |
  <Xudong: 1>                 |   <LeaveItToMe: 2>            |
  <MintyMeatRolls: 2>         |   <LotusFlowerCrisp: 1>       |
  <LeaveItToMe: 1>            |   <ChangingShifts: 1>         |
  <LotusFlowerCrisp: 2>       |   <StreamingSurge: 2>         |
  <ChangingShifts: 2>         |   <JueyunGuoba: 1>            |
  <StreamingSurge: 2>         |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 2>            |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>      |   <Starsigns: 1>              |
  <MondstadtHashBrown: 1>     |   <ThunderingPenance: 1>      |
  <Starsigns: 1>              | <Publicly Used Cards>         |
  <ThunderingPenance: 1>      |                               |
<Publicly Used Cards>         |                               |
  <Xudong: 1>                 |                               |
---------------------------------------------------------------
<Effects>
===============================================================
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @
```

I don't have many dices to use now, so let's end the round.

``` terminal
[info] :> Player1's Action Time!
Choices are:
@0: Card  |||  @1: Skill  |||  @2: Swap  |||  @3: EndRound

Please choose id (0-3): @3

#### Player1 Action: EndRoundAction:()

:> 
```

and the game continues like this until the end. Feel free to try it out yourself.

Don't forget to make use of `ba` to review the game history.
Or use `n` and `bn` to examine how the intermediate states transit from one to another.
