# Flow Chart

***Note That the Following Design Is Partially Adopted Into The Actual Project***

## General Phases

```mermaid
stateDiagram-v2
    cards   : Card Select Phase
    shand   : Starting Hand Select Phase
    roll    : Roll Phase
    action  : Action Phase
    state action {
        start  : Start Phase
        combat : Combat Phase
        [*]    --> start
        start  --> combat
        combat --> combat
        combat --> [*]
    }
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

`px,w,a` means player `x` is one of player 1 or player 2, and player `y` is the opponent. So both `p1,w,a` and `p2,a,w` can be fit into `px,w,a`.

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
    pxy     : Swap to Active Player

    state start {
        [*] --> px,w,w
        px,w,w --> [*]    : go through all pre-action-phase buffs
    }

    state combat {
        state pxy {
            cc : Clear Combat Log Cache

            [*]  --> Swap    : px,m,n or py,n,m
            Swap --> cc      : px,m,n
            cc   --> [*]     : px,m,n
        }

        [*]    -->  pxy
        pxy    -->  px,a,w   : translated
        pxy    -->  px,a,e   : translated
        px,a,w --> px,a,w    : fast action
        px,a,w --> py,w,a    : combat action
        px,a,w --> py,e,a    : end action
        px,a,e --> px,a,e    : fast action
        px,a,e --> pxy       : combat action
        px,a,e --> py,e,e    : end action
        py,w,a --> pxy
        py,e,a --> pxy
        py,e,e --> [*]       : py,w,w
    }

    [*]    --> start   : from Roll Phase
    start  --> combat  : px,a,w
    combat --> end     : py,w,w
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
        sq   --> [*]   : if all buffs checked
        sq   --> ab    : next buff
        ab   --> sq    : updated effect and game state
    }
    ex  : Effect Execution

    [*]  --> es    : an action contains a sequence of effects
    es   --> [*]   : no effects unexecuted
    es   --> pp    : pops an effect to execute
    pp   --> ex    : updated effect
    ex   --> es    : updated game state
```
