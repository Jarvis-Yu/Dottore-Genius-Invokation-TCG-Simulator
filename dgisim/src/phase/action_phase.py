from __future__ import annotations
from typing import Optional, cast

import dgisim.src.state.game_state as gm
import dgisim.src.phase.phase as ph
from dgisim.src.state.player_state import PlayerState
from dgisim.src.action import *
from dgisim.src.event.effect import DeathSwapPhaseEffect


class ActionPhase(ph.Phase):
    def _start_up_phase(self, game_state: gm.GameState) -> gm.GameState:
        # TODO: Handle before action buffs
        active_player_id = game_state.get_active_player_id()
        return game_state.factory().player(
            active_player_id,
            game_state.get_player(active_player_id).factory().phase(
                PlayerState.Act.ACTION_PHASE
            ).build()
        ).build()

    def _to_end_phase(self, game_state: gm.GameState) -> gm.GameState:
        active_player_id = game_state.get_active_player_id()
        return game_state.factory().phase(
            game_state.get_mode().end_phase()
        ).player(
            active_player_id,
            game_state.get_player(active_player_id).factory().phase(
                PlayerState.Act.PASSIVE_WAIT_PHASE
            ).build()
        ).other_player(
            active_player_id,
            game_state.get_other_player(active_player_id).factory().phase(
                PlayerState.Act.PASSIVE_WAIT_PHASE
            ).build()
        ).build()

    def _execute_effect(self, game_state: gm.GameState) -> gm.GameState:
        effect_stack, effect = game_state.get_effect_stack().pop()
        new_game_state = game_state.factory().effect_stack(effect_stack).build()
        return effect.execute(new_game_state)

    def _is_executing_effects(self, game_state: gm.GameState) -> bool:
        effect_stack = game_state.get_effect_stack()
        return not effect_stack.is_empty() \
            and not isinstance(effect_stack.peek(), DeathSwapPhaseEffect)

    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        p1p = p1.get_phase()
        p2p = p2.get_phase()
        if (p1p is PlayerState.Act.ACTION_PHASE and p2p is PlayerState.Act.PASSIVE_WAIT_PHASE) \
                or (p1p is PlayerState.Act.PASSIVE_WAIT_PHASE and p2p is PlayerState.Act.ACTION_PHASE):
            assert self._is_executing_effects(game_state)
            return self._execute_effect(game_state)
        elif p1p is PlayerState.Act.PASSIVE_WAIT_PHASE and p2p is PlayerState.Act.PASSIVE_WAIT_PHASE:
            return self._start_up_phase(game_state)
        elif p1p is PlayerState.Act.END_PHASE and p2p is PlayerState.Act.END_PHASE:
            return self._to_end_phase(game_state)
        raise Exception("Unknown Game State to process")

    def _handle_end_round(self, game_state: gm.GameState, pid: gm.GameState.Pid, action: EndRoundAction) -> gm.GameState:
        active_player_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        if other_player.get_phase() is PlayerState.Act.END_PHASE:
            other_player_new_phase = PlayerState.Act.END_PHASE
        elif other_player.get_phase() is PlayerState.Act.PASSIVE_WAIT_PHASE:
            other_player_new_phase = PlayerState.Act.ACTION_PHASE
        else:
            raise Exception(f"Unknown Game State to process {other_player.get_phase()}")
        if pid is active_player_id:
            return game_state.factory().active_player(
                active_player_id.other()
            ).player(
                active_player_id,
                active_player.factory().phase(
                    PlayerState.Act.END_PHASE
                ).build()
            ).other_player(
                active_player_id,
                other_player.factory().phase(
                    other_player_new_phase
                ).build()
            ).build()
        raise Exception("Unknown Game State to process")

    def _handle_game_action(self, game_state: gm.GameState, pid: gm.GameState.Pid, action: GameAction) -> gm.GameState:
        # TODO
        if isinstance(action, SkillAction):
            print("Got skill", action)
        return game_state

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.Pid, action: PlayerAction) -> gm.GameState:
        """
        TODO: Currently only allows player to end their round
        """
        if isinstance(action, EndRoundAction):
            # action = cast(EndRoundAction, action)
            return self._handle_end_round(game_state, pid, action)
        if isinstance(action, GameAction):
            # action = cast(GameAction, action)
            return self._handle_game_action(game_state, pid, action)
        raise Exception("Unknown Game State to process")

    def waiting_for(self, game_state: gm.GameState) -> Optional[gm.GameState.Pid]:
        """
        TODO: override this to handle death swap
        """
        effect_stack = game_state.get_effect_stack()
        # if no effects are to be executed or death swap phase is inserted
        if effect_stack.is_empty() \
                or isinstance(effect_stack.peek(), DeathSwapPhaseEffect):
            return super().waiting_for(game_state)
        else:
            return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ActionPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
