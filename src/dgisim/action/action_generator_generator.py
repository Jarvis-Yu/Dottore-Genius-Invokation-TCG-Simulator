from __future__ import annotations
from typing import TYPE_CHECKING

from .action_generator import ActionGenerator
from .action import *

if TYPE_CHECKING:
    from ..state.enums import PID
    from ..state.game_state import GameState

    from .types import DecidedChoiceType, GivenChoiceType

class SwapActGenGenerator:
    @classmethod
    def _choices_helper(
            cls,
            action_generator: ActionGenerator,
    ) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid

        action = action_generator.action
        if not action_generator._action_filled():
            assert type(action) is SwapAction \
                or type(action) is DeathSwapAction
            swappable_char_ids = [
                char.get_id()
                for char in game_state.get_player(pid).get_characters()
                if game_state.swap_checker().swap_details(pid, char.get_id()) is not None
            ]
            return tuple(
                char_id
                for char_id in swappable_char_ids
            )

        assert type(action) is SwapAction
        instruction = action_generator.instruction
        assert type(instruction) is DiceOnlyInstruction
        if instruction.dices is None:
            swap_details = game_state.swap_checker().swap_details(pid, action.char_id)
            assert swap_details is not None
            _, dices_cost = swap_details
            assert dices_cost is not None
            return dices_cost

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        action = action_generator.action
        assert type(action) is SwapAction \
            or type(action) is DeathSwapAction
        if action.char_id is None:
            assert type(player_choice) is int
            return replace(
                action_generator,
                action=replace(action, char_id=player_choice),
            )

        assert action_generator._action_filled()
        assert type(action) is SwapAction

        instruction = action_generator.instruction
        assert type(instruction) is DiceOnlyInstruction
        if instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    @classmethod
    def action_generator(
            cls,
            game_state: GameState,
            pid: PID,
    ) -> None | ActionGenerator:
        if not game_state.swap_checker().swappable(pid):
            return None
        if game_state.swap_checker().should_death_swap():
            return ActionGenerator(
                game_state=game_state,
                pid=pid,
                action=DeathSwapAction._all_none(),
                instruction=None,
                _choices_helper=cls._choices_helper,
                _fill_helper=cls._fill_helper,
            )
        else:
            return ActionGenerator(
                game_state=game_state,
                pid=pid,
                action=SwapAction._all_none(),
                instruction=DiceOnlyInstruction._all_none(),
                _choices_helper=cls._choices_helper,
                _fill_helper=cls._fill_helper,
            )
