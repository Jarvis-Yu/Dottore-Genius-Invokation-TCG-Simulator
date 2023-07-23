from typing import TYPE_CHECKING
from typing_extensions import override

from ...dices import ActualDices
from ...element import Element
from ...state.enums import Act
from ...state.game_state import GameState
from ..default.roll_phase import RollPhase as DefaultRollPhase

__all__ = [
    "RollPhase",
]


class RollPhase(DefaultRollPhase):
    @override
    def _get_all_dices_and_activate(self, game_state: GameState) -> GameState:
        return game_state.factory().f_player1(
            lambda p1: p1.factory()
            .phase(Act.ACTION_PHASE)
            .dice_reroll_chances(game_state.get_mode().dice_reroll_chances())
            .dices(ActualDices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            .build()
        ).f_player2(
            lambda p2: p2.factory()
            .phase(Act.ACTION_PHASE)
            .dice_reroll_chances(game_state.get_mode().dice_reroll_chances())
            .dices(ActualDices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            .build()
        ).build()
