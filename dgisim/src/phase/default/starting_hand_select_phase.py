from __future__ import annotations
from dataclasses import replace
from typing import Optional, TYPE_CHECKING

from .. import phase as ph
from ...effect import effect as eft

from ...action.action import PlayerAction, CharacterSelectAction
from ...action.action_generator import ActionGenerator
from ...effect.enums import Zone
from ...effect.structs import StaticTarget
from ...state.enums import Pid, Act

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...state.game_state import GameState

__all__ = [
    "StartingHandSelectPhase",
]


class StartingHandSelectPhase(ph.Phase):

    def _activate(self, game_state: GameState) -> GameState:
        return game_state.factory().player1(
            game_state.get_player1().factory().phase(Act.ACTION_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(Act.ACTION_PHASE).build()
        ).build()

    def _execute_effect(self, game_state: GameState) -> GameState:
        effect_stack, effect = game_state.get_effect_stack().pop()
        new_game_state = game_state.factory().effect_stack(effect_stack).build()
        return effect.execute(new_game_state)

    def _to_roll_phase(self, game_state: GameState) -> GameState:
        return game_state.factory().phase(
            game_state.get_mode().roll_phase()
        ).player1(
            game_state.get_player1().factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        if p1.is_passive_wait_phase() and p2.is_passive_wait_phase():
            return self._activate(game_state)
        elif game_state.get_effect_stack().is_not_empty():
            return self._execute_effect(game_state)
        elif p1.is_end_phase() and p2.is_end_phase():
            return self._to_roll_phase(game_state)
        else:  # pragma: no cover
            raise Exception("Unknown Game State to process")

    def _handle_picking_starting_hand(
            self,
            game_state: GameState,
            pid: Pid,
            action: CharacterSelectAction
    ) -> GameState:
        swap_action: CharacterSelectAction = action
        char_id = swap_action.char_id
        chars = game_state.get_player(pid).get_characters()
        if not chars.char_id_valid(char_id):  # pragma: no cover
            return game_state
        return game_state.factory().active_player_id(
            pid.other()
        ).f_player(
            pid,
            lambda p: p.factory().phase(
                Act.END_PHASE
            ).build()
        ).f_effect_stack(
            lambda es: es.push_one(
               eft.SwapCharacterEffect(StaticTarget(pid, Zone.CHARACTERS, char_id))
            )
        ).build()

    def step_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: PlayerAction
    ) -> Optional[GameState]:
        if isinstance(action, CharacterSelectAction):
            return self._handle_picking_starting_hand(game_state, pid, action)
        else:  # pragma: no cover
            raise Exception("Unknown Game State to process")

    def waiting_for(self, game_state: GameState) -> Optional[Pid]:
        effect_stack = game_state.get_effect_stack()
        # if no effects are to be executed or death swap phase is inserted
        if effect_stack.is_empty():
            return super().waiting_for(game_state)
        else:
            return None

    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        assert not action_generator.filled()
        game_state = action_generator.game_state
        pid = action_generator.pid
        action = action_generator.action
        assert type(action) is CharacterSelectAction and action.char_id is None
        characters = game_state.get_player(pid).get_characters()
        return tuple(character.get_id() for character in characters)

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        assert not action_generator.filled()
        action = action_generator.action
        assert type(action) is CharacterSelectAction and action.char_id is None
        assert isinstance(player_choice, int)
        return replace(
            action_generator,
            action=replace(
                action,
                char_id=player_choice,
            )
        )

    def action_generator(self, game_state: GameState, pid: Pid) -> ActionGenerator | None:
        if pid is not self.waiting_for(game_state):  # pragma: no cover
            return None
        return ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=CharacterSelectAction._all_none(),
            _choices_helper=self._choices_helper,
            _fill_helper=self._fill_helper,
        )
