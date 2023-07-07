# CLI Introduction

- [CLI Introduction](#cli-introduction)
  - [Show Case on How to Use the CLI](#show-case-on-how-to-use-the-cli)

## Show Case on How to Use the CLI

After setting up the environment following the instructions in the main [README](../README.md),
you may run `./scripts/sh/cli.sh` under the project directory to start a CLI session.

Below shows some random CLI session as an example, comments are occasionally added
in the format of `// ...`.

Note that prompts are of format `:>` or `::>`.

```txt
$ ./scripts/sh/cli.sh 
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
Please choose id (0-2)
::> @1    // choose PVE mode, you are player1 by default, opponent is random agent
          // note that the prompt format is ::> here

// below prints the current game state
==================================================
<Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Passive Wait Phase>   | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <Keqing>                    |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
<Deck Cards>                  | <Deck Cards>                  |
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
  <SweetMadame: 2>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 2>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================

:> a    // enter command auto-step, skipping intermediate state-transitions that
        // doesn't require player input
        // note that the prompt format is :> here
        // when prompt is :> you are expected to input a command (details in command 'h')
        // when prompt is ::> you are expected to input according to hints given
<Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Action Phase>         |
<Card Redraw Chances: 1>      | <Card Redraw Chances: 1>      |
<Characters>                  | <Characters>                  |
  <Keqing>                    |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
  <ThunderingPenance: 2>      |   <ChangingShifts: 1>         |
  <SweetMadame: 1>            |   <StreamingSurge: 1>         |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <NorthernSmokedChicken: 1>  |   <Xudong: 1>                 |
<Deck Cards>                  |   <NorthernSmokedChicken: 1>  |
  <Xudong: 2>                 | <Deck Cards>                  |
  <MintyMeatRolls: 2>         |   <Xudong: 1>                 |
  <LeaveItToMe: 2>            |   <MintyMeatRolls: 1>         |
  <LotusFlowerCrisp: 2>       |   <LeaveItToMe: 2>            |
  <ChangingShifts: 2>         |   <LotusFlowerCrisp: 2>       |
  <StreamingSurge: 2>         |   <ChangingShifts: 1>         |
  <JueyunGuoba: 2>            |   <StreamingSurge: 1>         |
  <ColdBloodedStrike: 2>      |   <JueyunGuoba: 2>            |
  <MondstadtHashBrown: 1>     |   <ColdBloodedStrike: 2>      |
  <Starsigns: 2>              |   <MondstadtHashBrown: 2>     |
  <SweetMadame: 1>            |   <Starsigns: 2>              |
  <NorthernSmokedChicken: 1>  |   <ThunderingPenance: 2>      |
  <MushroomPizza: 2>          |   <SweetMadame: 2>            |
<Publicly Used Cards>         |   <NorthernSmokedChicken: 1>  |
                              |   <MushroomPizza: 2>          |
                              | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
Choices are:
@0: SELECT_CARDS  |||  @1: END_ROUND
Please choose id (0-1)
::> @0    // choose to redraw some cards

Selections are:
@0: <ThunderingPenance, 2>  |||  @1: <SweetMadame, 1>  |||  @2: <MondstadtHashBrown, 1>  |||  @3: <NorthernSmokedChicken, 1>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 0:1, 3:1

#### Player1 Action: CardsSelectAction[<ThunderingPenance>: 1; <NorthernSmokedChicken>: 1; ]

:>     // no command is input means repeat last valid command, in this case, is auto-step
<Mode: DefaultMode>  <Phase: CardSelectPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: End Phase>            | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 1>      |
<Characters>                  | <Characters>                  |
  <Keqing>                    |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <ThunderingPenance: 1>      |   <Xudong: 1>                 |
  <SweetMadame: 1>            |   <NorthernSmokedChicken: 1>  |
<Deck Cards>                  | <Deck Cards>                  |
  <Xudong: 2>                 |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player2 Action: CardsSelectAction[<NorthernSmokedChicken>: 1; ]

:> 
<Mode: DefaultMode>  <Phase: StartingHandSelectPhase>  <Round: 0>
-----------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <Keqing>                    |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
  <ChangingShifts: 1>         |   <Xudong: 1>                 |
  <JueyunGuoba: 1>            |   <MintyMeatRolls: 1>         |
  <MondstadtHashBrown: 1>     |   <NorthernSmokedChicken: 1>  |
  <ThunderingPenance: 1>      |   <ChangingShifts: 1>         |
  <SweetMadame: 1>            |   <StreamingSurge: 1>         |
<Deck Cards>                  | <Deck Cards>                  |
  <Xudong: 2>                 |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
-----------------------------------------------------------------
<Effects>
=================================================================
Choices are:
@0: 1  |||  @1: 2  |||  @2: 3
Please choose id (0-2)
::> @0

#### Player1 Action: CharacterSelectAction:(char_id=1)

:> 
<Mode: DefaultMode>  <Phase: StartingHandSelectPhase>  <Round: 0>
-----------------------------------------------------------------
<Player: Player1>             | <Player: *Player2>            |
<Phase: End Phase>            | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <RhodeiaOfLoch>             |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
<Hand Cards>                  | <Hand Cards>                  |
  <ChangingShifts: 1>         |   <Xudong: 1>                 |
  <JueyunGuoba: 1>            |   <MintyMeatRolls: 1>         |
  <MondstadtHashBrown: 1>     |   <NorthernSmokedChicken: 1>  |
  <ThunderingPenance: 1>      |   <ChangingShifts: 1>         |
  <SweetMadame: 1>            |   <StreamingSurge: 1>         |
<Deck Cards>                  | <Deck Cards>                  |
  <Xudong: 2>                 |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
-----------------------------------------------------------------
<Effects>
=================================================================
#### Player2 Action: CharacterSelectAction:(char_id=2)

:> 
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <HYDRO: 1>                  |   <OMNI: 2>                   |
  <GEO: 1>                    |   <GEO: 1>                    |
  <CRYO: 1>                   |   <CRYO: 1>                   |
  <ELECTRO: 5>                |   <ELECTRO: 3>                |
<Hand Cards>                  |   <PYRO: 1>                   |
  <ChangingShifts: 1>         | <Hand Cards>                  |
  <JueyunGuoba: 1>            |   <Xudong: 1>                 |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <ThunderingPenance: 1>      |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>            |   <ChangingShifts: 1>         |
<Deck Cards>                  |   <StreamingSurge: 1>         |
  <Xudong: 2>                 | <Deck Cards>                  |
  <MintyMeatRolls: 2>         |   <Xudong: 1>                 |
  <LeaveItToMe: 2>            |   <MintyMeatRolls: 1>         |
  <LotusFlowerCrisp: 2>       |   <LeaveItToMe: 2>            |
  <ChangingShifts: 1>         |   <LotusFlowerCrisp: 2>       |
  <StreamingSurge: 2>         |   <ChangingShifts: 1>         |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
  <ColdBloodedStrike: 2>      |   <JueyunGuoba: 2>            |
  <MondstadtHashBrown: 1>     |   <ColdBloodedStrike: 2>      |
  <Starsigns: 2>              |   <MondstadtHashBrown: 2>     |
  <ThunderingPenance: 1>      |   <Starsigns: 2>              |
  <SweetMadame: 1>            |   <ThunderingPenance: 2>      |
  <NorthernSmokedChicken: 2>  |   <SweetMadame: 2>            |
  <MushroomPizza: 2>          |   <NorthernSmokedChicken: 1>  |
<Publicly Used Cards>         |   <MushroomPizza: 2>          |
                              | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
Choices are:
@0: SELECT_DICES  |||  @1: END_ROUND
Please choose id (0-1)
::> @0

Selections are:
@1: <HYDRO, 1>  |||  @2: <GEO, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 5>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 1:100    // deliberate faulty input, player doesn't have 100 HYDO dices

[error] -- Last input is invalid!
Selections are:
@1: <HYDRO, 1>  |||  @2: <GEO, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 5>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 5:1    // deliberate faulty input, player doesn't have die with index @5

[error] -- Last input is invalid!
Selections are:
@1: <HYDRO, 1>  |||  @2: <GEO, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 5>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 1:1, 2:1    // finally I gave some correct input

#### Player1 Action: DicesSelectAction[<HYDRO>: 1; <GEO>: 1; ]

:> 
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: End Phase>            | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <GEO: 1>                    |   <GEO: 1>                    |
  <CRYO: 1>                   |   <CRYO: 1>                   |
  <ELECTRO: 5>                |   <ELECTRO: 3>                |
<Hand Cards>                  |   <PYRO: 1>                   |
  <ChangingShifts: 1>         | <Hand Cards>                  |
  <JueyunGuoba: 1>            |   <Xudong: 1>                 |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <ThunderingPenance: 1>      |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>            |   <ChangingShifts: 1>         |
<Deck Cards>                  |   <StreamingSurge: 1>         |
  <Xudong: 2>                 | <Deck Cards>                  |
  <MintyMeatRolls: 2>         |   <Xudong: 1>                 |
  <LeaveItToMe: 2>            |   <MintyMeatRolls: 1>         |
  <LotusFlowerCrisp: 2>       |   <LeaveItToMe: 2>            |
  <ChangingShifts: 1>         |   <LotusFlowerCrisp: 2>       |
  <StreamingSurge: 2>         |   <ChangingShifts: 1>         |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
  <ColdBloodedStrike: 2>      |   <JueyunGuoba: 2>            |
  <MondstadtHashBrown: 1>     |   <ColdBloodedStrike: 2>      |
  <Starsigns: 2>              |   <MondstadtHashBrown: 2>     |
  <ThunderingPenance: 1>      |   <Starsigns: 2>              |
  <SweetMadame: 1>            |   <ThunderingPenance: 2>      |
  <NorthernSmokedChicken: 2>  |   <SweetMadame: 2>            |
  <MushroomPizza: 2>          |   <NorthernSmokedChicken: 1>  |
<Publicly Used Cards>         |   <MushroomPizza: 2>          |
                              | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player2 Action: DicesSelectAction[<OMNI>: 1; ]

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <GEO: 1>                    |   <GEO: 1>                    |
  <CRYO: 1>                   |   <CRYO: 1>                   |
  <ELECTRO: 5>                |   <ELECTRO: 3>                |
<Hand Cards>                  |   <PYRO: 1>                   |
  <ChangingShifts: 1>         | <Hand Cards>                  |
  <JueyunGuoba: 1>            |   <Xudong: 1>                 |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <ThunderingPenance: 1>      |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>            |   <ChangingShifts: 1>         |
<Deck Cards>                  |   <StreamingSurge: 1>         |
  <Xudong: 2>                 | <Deck Cards>                  |
  <MintyMeatRolls: 2>         |   <Xudong: 1>                 |
  <LeaveItToMe: 2>            |   <MintyMeatRolls: 1>         |
  <LotusFlowerCrisp: 2>       |   <LeaveItToMe: 2>            |
  <ChangingShifts: 1>         |   <LotusFlowerCrisp: 2>       |
  <StreamingSurge: 2>         |   <ChangingShifts: 1>         |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
  <ColdBloodedStrike: 2>      |   <JueyunGuoba: 2>            |
  <MondstadtHashBrown: 1>     |   <ColdBloodedStrike: 2>      |
  <Starsigns: 2>              |   <MondstadtHashBrown: 2>     |
  <ThunderingPenance: 1>      |   <Starsigns: 2>              |
  <SweetMadame: 1>            |   <ThunderingPenance: 2>      |
  <NorthernSmokedChicken: 2>  |   <SweetMadame: 2>            |
  <MushroomPizza: 2>          |   <NorthernSmokedChicken: 1>  |
<Publicly Used Cards>         |   <MushroomPizza: 2>          |
                              | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
Choices are:
@0: PLAY_CARD  |||  @1: CAST_SKILL  |||  @2: SWAP_CHARACTER  |||  @3: ELEMENTAL_TUNING  |||  @4: END_ROUND
Please choose id (0-4)
::> @1

Choices are:
@0: NORMAL_ATTACK  |||  @1: ELEMENTAL_SKILL1
Please choose id (0-1)
::> @1

[info] -- You need to pay for [('ELECTRO', '3')]
[info] -- auto-choice is [('ELECTRO', '3')]
[info] -- Enter nothing if you agree with the auto-choice
Selections are:
@0: <OMNI, 1>  |||  @2: <GEO, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 5>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 0:1, 2:1, 3:1    // give some faulty input as an example

[error] -- [('OMNI', '1'), ('GEO', '1'), ('CRYO', '1')] not valid
[info] -- auto-choice is [('ELECTRO', '3')]
[info] -- Enter nothing if you agree with the auto-choice
Selections are:
@0: <OMNI, 1>  |||  @2: <GEO, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 5>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::>     // entered nothing to use suggested dices

#### Player1 Action: <CharacterSkill.ELEMENTAL_SKILL1, DiceOnlyInstruction:(dices=[('ELECTRO', '3')])>

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: Player1>             | <Player: *Player2>            |
<Phase: Passive Wait Phase>   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: [ELECTRO]>         |
    <HP: 10/10>               |     <HP: 7/10>                |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <GEO: 1>                    |   <GEO: 1>                    |
  <CRYO: 1>                   |   <CRYO: 1>                   |
  <ELECTRO: 2>                |   <ELECTRO: 3>                |
<Hand Cards>                  |   <PYRO: 1>                   |
  <MondstadtHashBrown: 1>     | <Hand Cards>                  |
  <ThunderingPenance: 1>      |   <Xudong: 1>                 |
  <SweetMadame: 1>            |   <MintyMeatRolls: 1>         |
  <ChangingShifts: 1>         |   <NorthernSmokedChicken: 1>  |
  <LightningStiletto: 1>      |   <ChangingShifts: 1>         |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
<Deck Cards>                  | <Deck Cards>                  |
  <Xudong: 2>                 |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player2 Action: ElementalTuningAction:(card=<class 'src.dgisim.card.card.ChangingShifts'>, dice_elem=Element.ELECTRO)

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: Player1>             | <Player: *Player2>            |
<Phase: Passive Wait Phase>   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: [ELECTRO]>         |
    <HP: 10/10>               |     <HP: 7/10>                |
    <Energy: 0/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <GEO: 1>                    |   <HYDRO: 1>                  |
  <CRYO: 1>                   |   <GEO: 1>                    |
  <ELECTRO: 2>                |   <CRYO: 1>                   |
<Hand Cards>                  |   <ELECTRO: 2>                |
  <MondstadtHashBrown: 1>     |   <PYRO: 1>                   |
  <ThunderingPenance: 1>      | <Hand Cards>                  |
  <SweetMadame: 1>            |   <Xudong: 1>                 |
  <ChangingShifts: 1>         |   <MintyMeatRolls: 1>         |
  <LightningStiletto: 1>      |   <NorthernSmokedChicken: 1>  |
  <JueyunGuoba: 1>            |   <StreamingSurge: 1>         |
<Deck Cards>                  | <Deck Cards>                  |
  <Xudong: 2>                 |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>         |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>            |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>       |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>         |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>         |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>            |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>      |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>     |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>              |   <Starsigns: 2>              |
  <ThunderingPenance: 1>      |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>            |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>  |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>          |   <MushroomPizza: 2>          |
<Publicly Used Cards>         | <Publicly Used Cards>         |
---------------------------------------------------------------
<Effects>
===============================================================
#### Player2 Action: <CharacterSkill.NORMAL_ATTACK, DiceOnlyInstruction:(dices=[('HYDRO', '1'), ('GEO', '1'), ('CRYO', '1')])>

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: [HYDRO]>           |     <Aura: []>                |
    <HP: 9/10>                |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: [ELECTRO]>         |
    <HP: 10/10>               |     <HP: 7/10>                |
    <Energy: 0/3>             |     <Energy: 1/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <GEO: 1>                    |   <ELECTRO: 2>                |
  <CRYO: 1>                   |   <PYRO: 1>                   |
  <ELECTRO: 2>                | <Hand Cards>                  |
<Hand Cards>                  |   <Xudong: 1>                 |
  <MondstadtHashBrown: 1>     |   <MintyMeatRolls: 1>         |
  <ThunderingPenance: 1>      |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>            |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>         | <Deck Cards>                  |
  <LightningStiletto: 1>      |   <Xudong: 1>                 |
  <JueyunGuoba: 1>            |   <MintyMeatRolls: 1>         |
<Deck Cards>                  |   <LeaveItToMe: 2>            |
  <Xudong: 2>                 |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>         |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>            |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>       |   <JueyunGuoba: 2>            |
  <ChangingShifts: 1>         |   <ColdBloodedStrike: 2>      |
  <StreamingSurge: 2>         |   <MondstadtHashBrown: 2>     |
  <JueyunGuoba: 1>            |   <Starsigns: 2>              |
  <ColdBloodedStrike: 2>      |   <ThunderingPenance: 2>      |
  <MondstadtHashBrown: 1>     |   <SweetMadame: 2>            |
  <Starsigns: 2>              |   <NorthernSmokedChicken: 1>  |
  <ThunderingPenance: 1>      |   <MushroomPizza: 2>          |
  <SweetMadame: 1>            | <Publicly Used Cards>         |
  <NorthernSmokedChicken: 2>  |                               |
  <MushroomPizza: 2>          |                               |
<Publicly Used Cards>         |                               |
---------------------------------------------------------------
<Effects>
===============================================================
Choices are:
@0: PLAY_CARD  |||  @1: CAST_SKILL  |||  @2: SWAP_CHARACTER  |||  @3: ELEMENTAL_TUNING  |||  @4: END_ROUND
Please choose id (0-4)
::> @3

Choices are:
@0: MondstadtHashBrown  |||  @1: ThunderingPenance  |||  @2: SweetMadame  |||  @3: ChangingShifts  |||  @4: LightningStiletto  |||  @5: JueyunGuoba
Please choose id (0-5)
::> @5

Choices are:
@0: GEO  |||  @1: CRYO
Please choose id (0-1)
::> @0

#### Player1 Action: ElementalTuningAction:(card=<class 'src.dgisim.card.card.JueyunGuoba'>, dice_elem=Element.GEO)

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
---------------------------------------------------------------
<Player: *Player1>            | <Player: Player2>             |
<Phase: Action Phase>         | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>      | <Card Redraw Chances: 0>      |
<Characters>                  | <Characters>                  |
  <*Keqing>                   |   <Keqing>                    |
    <id: 1>                   |     <id: 1>                   |
    <Aura: [HYDRO]>           |     <Aura: []>                |
    <HP: 9/10>                |     <HP: 10/10>               |
    <Energy: 1/3>             |     <Energy: 0/3>             |
    <Talents>                 |     <Talents>                 |
      <KeqingTalent(0)>       |       <KeqingTalent(0)>       |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <RhodeiaOfLoch>             |   <*RhodeiaOfLoch>            |
    <id: 2>                   |     <id: 2>                   |
    <Aura: []>                |     <Aura: [ELECTRO]>         |
    <HP: 10/10>               |     <HP: 7/10>                |
    <Energy: 0/3>             |     <Energy: 1/3>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
  <Kaeya>                     |   <Kaeya>                     |
    <id: 3>                   |     <id: 3>                   |
    <Aura: []>                |     <Aura: []>                |
    <HP: 10/10>               |     <HP: 10/10>               |
    <Energy: 0/2>             |     <Energy: 0/2>             |
    <Talents>                 |     <Talents>                 |
    <Equipments>              |     <Equipments>              |
    <Statuses>                |     <Statuses>                |
<Combat Statuses: []>         | <Combat Statuses: []>         |
<Summons>                     | <Summons>                     |
<Supports>                    | <Supports>                    |
<Dices>                       | <Dices>                       |
  <OMNI: 1>                   |   <OMNI: 2>                   |
  <CRYO: 1>                   |   <ELECTRO: 2>                |
  <ELECTRO: 3>                |   <PYRO: 1>                   |
<Hand Cards>                  | <Hand Cards>                  |
  <MondstadtHashBrown: 1>     |   <Xudong: 1>                 |
  <ThunderingPenance: 1>      |   <MintyMeatRolls: 1>         |
  <SweetMadame: 1>            |   <NorthernSmokedChicken: 1>  |
  <ChangingShifts: 1>         |   <StreamingSurge: 1>         |
  <LightningStiletto: 1>      | <Deck Cards>                  |
<Deck Cards>                  |   <Xudong: 1>                 |
  <Xudong: 2>                 |   <MintyMeatRolls: 1>         |
  <MintyMeatRolls: 2>         |   <LeaveItToMe: 2>            |
  <LeaveItToMe: 2>            |   <LotusFlowerCrisp: 2>       |
  <LotusFlowerCrisp: 2>       |   <ChangingShifts: 1>         |
  <ChangingShifts: 1>         |   <StreamingSurge: 1>         |
  <StreamingSurge: 2>         |   <JueyunGuoba: 2>            |
  <JueyunGuoba: 1>            |   <ColdBloodedStrike: 2>      |
  <ColdBloodedStrike: 2>      |   <MondstadtHashBrown: 2>     |
  <MondstadtHashBrown: 1>     |   <Starsigns: 2>              |
  <Starsigns: 2>              |   <ThunderingPenance: 2>      |
  <ThunderingPenance: 1>      |   <SweetMadame: 2>            |
  <SweetMadame: 1>            |   <NorthernSmokedChicken: 1>  |
  <NorthernSmokedChicken: 2>  |   <MushroomPizza: 2>          |
  <MushroomPizza: 2>          | <Publicly Used Cards>         |
<Publicly Used Cards>         |                               |
---------------------------------------------------------------
<Effects>
===============================================================
Choices are:
@0: PLAY_CARD  |||  @1: CAST_SKILL  |||  @2: SWAP_CHARACTER  |||  @3: ELEMENTAL_TUNING  |||  @4: END_ROUND
Please choose id (0-4)
::> @0

Choices are:
@0: MondstadtHashBrown  |||  @1: ThunderingPenance  |||  @2: SweetMadame  |||  @3: ChangingShifts  |||  @4: LightningStiletto
Please choose id (0-4)
::> @1

[info] -- You need to pay for [('ELECTRO', '3')]
[info] -- auto-choice is [('ELECTRO', '3')]
[info] -- Enter nothing if you agree with the auto-choice
Selections are:
@0: <OMNI, 1>  |||  @3: <CRYO, 1>  |||  @4: <ELECTRO, 3>
e.g. input "0:2,4:1,3:1" means choosing 2 of @0, 1 of @4 and 1 of @3
::> 0:1, 4:2    // this is not optimal choice, just to show that you can make the choice

#### Player1 Action: <ThunderingPenance, DiceOnlyInstruction:(dices=[('OMNI', '1'), ('ELECTRO', '2')])>

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: Passive Wait Phase>          | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <Keqing>                    |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 9/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 0/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <*RhodeiaOfLoch>            |
      <KeqingElectroInfusion(3)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 2>                   |
<Dices>                              |   <ELECTRO: 2>                |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <ELECTRO: 1>                       | <Hand Cards>                  |
<Hand Cards>                         |   <Xudong: 1>                 |
  <MondstadtHashBrown: 1>            |   <MintyMeatRolls: 1>         |
  <SweetMadame: 1>                   |   <NorthernSmokedChicken: 1>  |
  <ChangingShifts: 1>                |   <StreamingSurge: 1>         |
<Deck Cards>                         | <Deck Cards>                  |
  <Xudong: 2>                        |   <Xudong: 1>                 |
  <MintyMeatRolls: 2>                |   <MintyMeatRolls: 1>         |
  <LeaveItToMe: 2>                   |   <LeaveItToMe: 2>            |
  <LotusFlowerCrisp: 2>              |   <LotusFlowerCrisp: 2>       |
  <ChangingShifts: 1>                |   <ChangingShifts: 1>         |
  <StreamingSurge: 2>                |   <StreamingSurge: 1>         |
  <JueyunGuoba: 1>                   |   <JueyunGuoba: 2>            |
  <ColdBloodedStrike: 2>             |   <ColdBloodedStrike: 2>      |
  <MondstadtHashBrown: 1>            |   <MondstadtHashBrown: 2>     |
  <Starsigns: 2>                     |   <Starsigns: 2>              |
  <ThunderingPenance: 1>             |   <ThunderingPenance: 2>      |
  <SweetMadame: 1>                   |   <SweetMadame: 2>            |
  <NorthernSmokedChicken: 2>         |   <NorthernSmokedChicken: 1>  |
  <MushroomPizza: 2>                 |   <MushroomPizza: 2>          |
<Publicly Used Cards>                | <Publicly Used Cards>         |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: SwapAction:(char_id=1, instruction=DiceOnlyInstruction:(dices=[('PYRO', '1')]))

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: Action Phase>                | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 9/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 0/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(3)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 2>                   |
<Dices>                              |   <ELECTRO: 2>                |
  <CRYO: 1>                          | <Hand Cards>                  |
  <ELECTRO: 1>                       |   <Xudong: 1>                 |
<Hand Cards>                         |   <MintyMeatRolls: 1>         |
  <MondstadtHashBrown: 1>            |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>                | <Deck Cards>                  |
<Deck Cards>                         |   <Xudong: 1>                 |
  <Xudong: 2>                        |   <MintyMeatRolls: 1>         |
  <MintyMeatRolls: 2>                |   <LeaveItToMe: 2>            |
  <LeaveItToMe: 2>                   |   <LotusFlowerCrisp: 2>       |
  <LotusFlowerCrisp: 2>              |   <ChangingShifts: 1>         |
  <ChangingShifts: 1>                |   <StreamingSurge: 1>         |
  <StreamingSurge: 2>                |   <JueyunGuoba: 2>            |
  <JueyunGuoba: 1>                   |   <ColdBloodedStrike: 2>      |
  <ColdBloodedStrike: 2>             |   <MondstadtHashBrown: 2>     |
  <MondstadtHashBrown: 1>            |   <Starsigns: 2>              |
  <Starsigns: 2>                     |   <ThunderingPenance: 2>      |
  <ThunderingPenance: 1>             |   <SweetMadame: 2>            |
  <SweetMadame: 1>                   |   <NorthernSmokedChicken: 1>  |
  <NorthernSmokedChicken: 2>         |   <MushroomPizza: 2>          |
  <MushroomPizza: 2>                 | <Publicly Used Cards>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
Choices are:
@0: PLAY_CARD  |||  @1: SWAP_CHARACTER  |||  @2: ELEMENTAL_TUNING  |||  @3: END_ROUND
Please choose id (0-3)
::> @3

#### Player1 Action: EndRoundAction:()

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 9/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 0/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(3)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 2>                   |
<Dices>                              |   <ELECTRO: 2>                |
  <CRYO: 1>                          | <Hand Cards>                  |
  <ELECTRO: 1>                       |   <Xudong: 1>                 |
<Hand Cards>                         |   <MintyMeatRolls: 1>         |
  <MondstadtHashBrown: 1>            |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>                | <Deck Cards>                  |
<Deck Cards>                         |   <Xudong: 1>                 |
  <Xudong: 2>                        |   <MintyMeatRolls: 1>         |
  <MintyMeatRolls: 2>                |   <LeaveItToMe: 2>            |
  <LeaveItToMe: 2>                   |   <LotusFlowerCrisp: 2>       |
  <LotusFlowerCrisp: 2>              |   <ChangingShifts: 1>         |
  <ChangingShifts: 1>                |   <StreamingSurge: 1>         |
  <StreamingSurge: 2>                |   <JueyunGuoba: 2>            |
  <JueyunGuoba: 1>                   |   <ColdBloodedStrike: 2>      |
  <ColdBloodedStrike: 2>             |   <MondstadtHashBrown: 2>     |
  <MondstadtHashBrown: 1>            |   <Starsigns: 2>              |
  <Starsigns: 2>                     |   <ThunderingPenance: 2>      |
  <ThunderingPenance: 1>             |   <SweetMadame: 2>            |
  <SweetMadame: 1>                   |   <NorthernSmokedChicken: 1>  |
  <NorthernSmokedChicken: 2>         |   <MushroomPizza: 2>          |
  <MushroomPizza: 2>                 | <Publicly Used Cards>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: <CharacterSkill.NORMAL_ATTACK, DiceOnlyInstruction:(dices=[('ELECTRO', '2'), ('OMNI', '1')])>

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(3)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              | <Hand Cards>                  |
  <CRYO: 1>                          |   <Xudong: 1>                 |
  <ELECTRO: 1>                       |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 1>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <MintyMeatRolls: 1>         |
  <Xudong: 2>                        |   <LeaveItToMe: 2>            |
  <MintyMeatRolls: 2>                |   <LotusFlowerCrisp: 2>       |
  <LeaveItToMe: 2>                   |   <ChangingShifts: 1>         |
  <LotusFlowerCrisp: 2>              |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>                |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 2>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 2>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |                               |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: <MintyMeatRolls, StaticTargetInstruction:(dices=[('OMNI', '1')], target=StaticTarget(pid=<PID.P2: 2>, zone=<ZONE.CHARACTERS: 'Characters'>, id=1))>

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |       <MintyMeatRolls(3)>     |
      <KeqingElectroInfusion(3)(1)>  |       <Satiated>              |
  <RhodeiaOfLoch>                    |   <RhodeiaOfLoch>             |
    <id: 2>                          |     <id: 2>                   |
    <Aura: []>                       |     <Aura: [ELECTRO]>         |
    <HP: 10/10>                      |     <HP: 4/10>                |
    <Energy: 0/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
    <Equipments>                     |     <Equipments>              |
    <Statuses>                       |     <Statuses>                |
  <Kaeya>                            |   <Kaeya>                     |
    <id: 3>                          |     <id: 3>                   |
    <Aura: []>                       |     <Aura: []>                |
    <HP: 10/10>                      |     <HP: 10/10>               |
    <Energy: 0/2>                    |     <Energy: 0/2>             |
    <Talents>                        |     <Talents>                 |
    <Equipments>                     |     <Equipments>              |
    <Statuses>                       |     <Statuses>                |
<Combat Statuses: []>                | <Combat Statuses: []>         |
<Summons>                            | <Summons>                     |
<Supports>                           | <Supports>                    |
<Dices>                              | <Dices>                       |
  <CRYO: 1>                          | <Hand Cards>                  |
  <ELECTRO: 1>                       |   <Xudong: 1>                 |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 1>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <MintyMeatRolls: 1>         |
  <Xudong: 2>                        |   <LeaveItToMe: 2>            |
  <MintyMeatRolls: 2>                |   <LotusFlowerCrisp: 2>       |
  <LeaveItToMe: 2>                   |   <ChangingShifts: 1>         |
  <LotusFlowerCrisp: 2>              |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>                |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 2>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 2>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: EndRoundAction:()

:> 
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: Action Phase>                | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
Choices are:
@0: SELECT_DICES  |||  @1: END_ROUND
Please choose id (0-1)
::> @1    // not doing reroll here

#### Player1 Action: EndRoundAction:()

:> 
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: EndRoundAction:()

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: Action Phase>                | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
Choices are:
@0: PLAY_CARD  |||  @1: SWAP_CHARACTER  |||  @2: ELEMENTAL_TUNING  |||  @3: END_ROUND
Please choose id (0-3)
::> @3 

#### Player1 Action: EndRoundAction:()

:> ba    // browse history, backward auto-step
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: EndRoundAction:()
#### [117/121] in game history

:> 
<Mode: DefaultMode>  <Phase: RollPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: Action Phase>                | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player1 Action: EndRoundAction:()
#### [116/121] in game history

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 0>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |       <MintyMeatRolls(3)>     |
      <KeqingElectroInfusion(3)(1)>  |       <Satiated>              |
  <RhodeiaOfLoch>                    |   <RhodeiaOfLoch>             |
    <id: 2>                          |     <id: 2>                   |
    <Aura: []>                       |     <Aura: [ELECTRO]>         |
    <HP: 10/10>                      |     <HP: 4/10>                |
    <Energy: 0/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
    <Equipments>                     |     <Equipments>              |
    <Statuses>                       |     <Statuses>                |
  <Kaeya>                            |   <Kaeya>                     |
    <id: 3>                          |     <id: 3>                   |
    <Aura: []>                       |     <Aura: []>                |
    <HP: 10/10>                      |     <HP: 10/10>               |
    <Energy: 0/2>                    |     <Energy: 0/2>             |
    <Talents>                        |     <Talents>                 |
    <Equipments>                     |     <Equipments>              |
    <Statuses>                       |     <Statuses>                |
<Combat Statuses: []>                | <Combat Statuses: []>         |
<Summons>                            | <Summons>                     |
<Supports>                           | <Supports>                    |
<Dices>                              | <Dices>                       |
  <CRYO: 1>                          | <Hand Cards>                  |
  <ELECTRO: 1>                       |   <Xudong: 1>                 |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 1>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <MintyMeatRolls: 1>         |
  <Xudong: 2>                        |   <LeaveItToMe: 2>            |
  <MintyMeatRolls: 2>                |   <LotusFlowerCrisp: 2>       |
  <LeaveItToMe: 2>                   |   <ChangingShifts: 1>         |
  <LotusFlowerCrisp: 2>              |   <StreamingSurge: 1>         |
  <ChangingShifts: 1>                |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 2>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 2>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: EndRoundAction:()
#### [91/121] in game history

:> a    // forward auto-step again
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: *Player1>                   | <Player: Player2>             |
<Phase: Action Phase>                | <Phase: Passive Wait Phase>   |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player1 Action: EndRoundAction:()
#### [120/121] in game history

:> 
<Mode: DefaultMode>  <Phase: ActionPhase>  <Round: 1>
----------------------------------------------------------------------
<Player: Player1>                    | <Player: *Player2>            |
<Phase: End Phase>                   | <Phase: Action Phase>         |
<Card Redraw Chances: 0>             | <Card Redraw Chances: 0>      |
<Characters>                         | <Characters>                  |
  <*Keqing>                          |   <*Keqing>                   |
    <id: 1>                          |     <id: 1>                   |
    <Aura: [HYDRO]>                  |     <Aura: []>                |
    <HP: 7/10>                       |     <HP: 10/10>               |
    <Energy: 2/3>                    |     <Energy: 1/3>             |
    <Talents>                        |     <Talents>                 |
      <KeqingTalent(0)>              |       <KeqingTalent(0)>       |
    <Equipments>                     |     <Equipments>              |
      <ThunderingPenance>            |     <Statuses>                |
    <Statuses>                       |   <RhodeiaOfLoch>             |
      <KeqingElectroInfusion(2)(1)>  |     <id: 2>                   |
  <RhodeiaOfLoch>                    |     <Aura: [ELECTRO]>         |
    <id: 2>                          |     <HP: 4/10>                |
    <Aura: []>                       |     <Energy: 1/3>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/3>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     |   <Kaeya>                     |
    <Statuses>                       |     <id: 3>                   |
  <Kaeya>                            |     <Aura: []>                |
    <id: 3>                          |     <HP: 10/10>               |
    <Aura: []>                       |     <Energy: 0/2>             |
    <HP: 10/10>                      |     <Talents>                 |
    <Energy: 0/2>                    |     <Equipments>              |
    <Talents>                        |     <Statuses>                |
    <Equipments>                     | <Combat Statuses: []>         |
    <Statuses>                       | <Summons>                     |
<Combat Statuses: []>                | <Supports>                    |
<Summons>                            | <Dices>                       |
<Supports>                           |   <OMNI: 1>                   |
<Dices>                              |   <HYDRO: 4>                  |
  <HYDRO: 1>                         |   <CRYO: 2>                   |
  <CRYO: 1>                          |   <PYRO: 1>                   |
  <DENDRO: 2>                        | <Hand Cards>                  |
  <PYRO: 2>                          |   <Xudong: 1>                 |
  <ANEMO: 2>                         |   <MintyMeatRolls: 1>         |
<Hand Cards>                         |   <NorthernSmokedChicken: 1>  |
  <MondstadtHashBrown: 1>            |   <StreamingSurge: 1>         |
  <Starsigns: 1>                     |   <MushroomPizza: 1>          |
  <SweetMadame: 1>                   | <Deck Cards>                  |
  <ChangingShifts: 2>                |   <Xudong: 1>                 |
<Deck Cards>                         |   <LeaveItToMe: 2>            |
  <Xudong: 2>                        |   <LotusFlowerCrisp: 2>       |
  <MintyMeatRolls: 2>                |   <ChangingShifts: 1>         |
  <LeaveItToMe: 2>                   |   <StreamingSurge: 1>         |
  <LotusFlowerCrisp: 2>              |   <JueyunGuoba: 2>            |
  <StreamingSurge: 2>                |   <ColdBloodedStrike: 2>      |
  <JueyunGuoba: 1>                   |   <MondstadtHashBrown: 2>     |
  <ColdBloodedStrike: 2>             |   <Starsigns: 2>              |
  <MondstadtHashBrown: 1>            |   <ThunderingPenance: 2>      |
  <Starsigns: 1>                     |   <SweetMadame: 2>            |
  <ThunderingPenance: 1>             |   <NorthernSmokedChicken: 1>  |
  <SweetMadame: 1>                   |   <MushroomPizza: 1>          |
  <NorthernSmokedChicken: 2>         | <Publicly Used Cards>         |
  <MushroomPizza: 2>                 |   <MintyMeatRolls: 1>         |
<Publicly Used Cards>                |                               |
  <ThunderingPenance: 1>             |                               |
----------------------------------------------------------------------
<Effects>
======================================================================
#### Player2 Action: <CharacterSkill.NORMAL_ATTACK, DiceOnlyInstruction:(dices=[('PYRO', '1'), ('CRYO', '1'), ('OMNI', '1')])>

:> q    // quit CLI
```

If you do want to learn more about how the state-machine (for this game) works,
I encourage you to use `n` and `bn` often to observe how `Effects` are processed.
