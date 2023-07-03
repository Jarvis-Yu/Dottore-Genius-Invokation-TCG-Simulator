from __future__ import annotations
from typing import TYPE_CHECKING

from ..phase import phase as ph

from ..dices import ActualDices
from ..element.element import Element
from ..state.enums import ACT

if TYPE_CHECKING:
    from ..state.game_state import GameState


class RollPhase(ph.Phase):
    _NUM_DICES = 8

    def _get_all_omni_and_to_action_phase(self, game_state: GameState) -> GameState:
        return game_state.factory().phase(
            game_state.get_mode().action_phase()
        ).player1(
            game_state.get_player1().factory()
            .phase(ACT.PASSIVE_WAIT_PHASE)
            .dices(ActualDices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            # .dices(ActualDices.from_random(RollPhase._NUM_DICES))
            .build()
        ).player2(
            game_state.get_player2().factory()
            .phase(ACT.PASSIVE_WAIT_PHASE)
            .dices(ActualDices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            # .dices(ActualDices.from_random(RollPhase._NUM_DICES))
            .build()
        ).build()

    def step(self, game_state: GameState) -> GameState:
        # if game_state.get_active_player().is_player1():
        #     p1_phase = PlayerState.act.ACTIVE_WAIT_PHASE
        #     p2_phase = PlayerState.act.PASSIVE_WAIT_PHASE
        # elif game_state.get_active_player().is_player2():
        #     p1_phase = PlayerState.act.PASSIVE_WAIT_PHASE
        #     p2_phase = PlayerState.act.ACTIVE_WAIT_PHASE
        # else:
        #     raise Exception("Undefined Player id")
        return self._get_all_omni_and_to_action_phase(game_state)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RollPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
