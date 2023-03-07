# Flow Chart

## General Phases

```mermaid
stateDiagram-v2
    cards   : Card Select Phase
    shand   : Starting Hand Select Phase
    roll    : Roll Phase
    action  : Action Phase
    end     : End Phase
    gameEnd : Game End Phase

    [*]     --> cards
    cards   --> shand
    shand   --> roll
    roll    --> action
    action  --> end
    action  --> gameEnd : if a player is defeated
    end     --> gameEnd : if a player is defeated or round limit is reached
    end     --> roll
    gameEnd --> [*]
```

## Action Phase

`p1,w,a` means this is player1's turn. Player1 is in waiting phase and player2 is in action phase.

- `a` is action phase
- `w` is waiting phase
- `e` is end phase

```mermaid
stateDiagram-v2
    start   : Start Phase
    combat  : Combat Phase
    end     : End Phase
    ds      : Death Swap Phase
    gameEnd : Game End Phase

    state combat {
        [*] --> p1,w,w    : given
        [*] --> p2,w,w    : given
        p1,w,w --> p1,a,w
        p2,w,w --> p2,w,a

        p1,a,w --> p1,a,w : fast action
        p1,a,w --> p2,w,a : combat action
        p1,a,w --> p2,e,a : end action

        p2,w,a --> p2,w,a : fast action
        p2,w,a --> p1,a,w : combat action
        p2,w,a --> p1,a,e : end action

        p2,e,a --> p2,e,a : any action
        p2,e,a --> p1,e,e : end action

        p1,a,e --> p1,a,e : any action
        p1,a,e --> p2,e,e : end action

        p1,e,e --> [*]    : p1,w,w
        p2,e,e --> [*]    : p2,w,w
    }

    [*]    --> start
    start  --> combat  : go through all pre-action-phase buffs
    combat --> end     : p1,w,w or p2,w,w
    combat --> ds      : if any action caused character death
    ds     --> ds      : if swap caused character death
    ds     --> combat  : back to last state
    combat --> gameEnd : if a player is defeated
```

## Action Execution Flow

Not that all effects after direct effect are executed only if their preconditions are satisfied. (e.g. action event matches, elemental reaction happens...)

```mermaid
stateDiagram-v2
    gs    : Some Game State in Action Phase
    de    : Direct Effect Execution
    eq    : Equipments Effect Execution
    sb    : Self Effect Execution
    tb    : Team Effect Execution
    sms   : Summons Effect Execution
    sps   : Supports Effect Execution
    ds    : Death Swap
    sw    : Swap Player Turn

    [*]  --> gs
    ds   --> de    : back
    ds   --> eq    : back
    ds   --> tb    : back
    ds   --> sb    : back
    ds   --> sms   : back
    ds   --> sps   : back
    de   --> ds    : new death
    ds   --> ds    : new death
    eq   --> ds    : new death
    sb   --> ds    : new death
    tb   --> ds    : new death
    sms  --> ds    : new death
    sps  --> ds    : new death
    gs   --> sw    : end action
    gs   --> de    : fast/combat action
    de   --> eq    : updates log
    eq   --> sb    : updates log
    sb   --> tb    : updates log
    tb   --> sms   : updates log
    sms  --> sps   : updates log
    sps  --> sw    : updates log
    sw   --> gs    : with a self/oppo as active player,\nand clear log
    sw   --> [*]   : if both player ends
```

## Action Execution in detail

An action consists of a number of effects, some are bounded to be executed together, some can be seperated.

In the chart below, `e` is used to denote a single effect or a sequence of effects inseperable, `es` is used to denote the rest of effects in the effect queue.

```mermaid
stateDiagram-v2
    es  : Pending Effects Check
    pp  : Preprocessing
    state pp {
        sq  : Ordered Buffs
        ab  : Add Buff To Effect

        [*]  --> sq
        sq   --> [*]   : if all buffs executed
        sq   --> ab    : next buff
        ab   --> sq    : updated effect and game state
    }
    ex  : Effect Execution

    [*]  --> es
    es   --> [*]   : no effects unexecuted
    es   --> pp    : pops an effect to execute
    pp   --> ex    : updated effect
    ex   --> es    : updated game state
```
