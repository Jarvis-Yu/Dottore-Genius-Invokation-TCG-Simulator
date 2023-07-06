"""
This file contains method classes that provide an optional ActionGenerator of a
particular type based on the GameState and PID passed in.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from ..helper.quality_of_life import just

from .action_generator import ActionGenerator
from .action import *

if TYPE_CHECKING:
    from ..state.enums import PID
    from ..state.game_state import GameState

    from .types import DecidedChoiceType, GivenChoiceType


class CardActGenGenerator:
    """
    This generates an ActionGenerator allowing the agent to choose which card to
    play.

    If there is no card that is playable for any reason, then None is returned.
    """
    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        assert not action_generator.filled()
        game_state = action_generator.game_state
        pid = action_generator.pid
        return tuple(
            card_type
            for card_type in game_state.get_player(pid).get_hand_cards()
            if card_type.strictly_usable(game_state, pid)
        )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        from ..card.card import Card
        assert not action_generator.filled()
        assert issubclass(player_choice, Card)  # type: ignore
        assert action_generator.game_state.card_checker().usable(
            action_generator.pid,
            player_choice,  # type: ignore
        )
        return just(player_choice.action_generator(  # type: ignore
            action_generator.game_state,
            action_generator.pid
        ))

    @classmethod
    def action_generator(
            cls,
            game_state: GameState,
            pid: PID,
    ) -> None | ActionGenerator:
        if not game_state.card_checker().playable(pid):
            return None
        return ActionGenerator(
            game_state=game_state,
            pid=pid,
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )


class SwapActGenGenerator:
    """
    This generates an ActionGenerator for ordinary SwapAction or DeathSwapAction
    based on the provided game state and pid.

    If a swap action is unavailable for the reasons below, then None is returned:

    1. there is no alive ally to swap to
    2. there is not enough dice for any swap
    3. it's not this player's turn (TODO)
    """
    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
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


class SkillActGenGenerator:
    """
    This generates an ActionGenerator allowing the agnet to choose which skill
    to cast.

    If there is no skill castable for any reason, then None is returned.
    """
    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        game_state = action_generator.game_state
        pid = action_generator.pid
        active_character = game_state.get_player(pid).just_get_active_character()

        action = action_generator.action
        assert type(action) is SkillAction
        if action.skill is None:
            skills = active_character.skills()
            return tuple(
                skill
                for skill in skills
                if game_state.skill_checker().usable(
                    pid, active_character.get_id(), skill
                ) is not None
            )

        assert action_generator._action_filled()
        instruction = action_generator.instruction
        assert type(instruction) is DiceOnlyInstruction
        if instruction.dices is None:
            retval = game_state.skill_checker().usable(pid, active_character.get_id(), action.skill)
            assert retval is not None
            _, dices = retval
            return dices

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
        assert type(action) is SkillAction
        if action.skill is None:
            assert type(player_choice) is CharacterSkill
            return replace(
                action_generator,
                action=replace(action, skill=player_choice),
            )

        instruction = action_generator.instruction
        assert type(instruction) is DiceOnlyInstruction
        if instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            game_state = action_generator.game_state
            pid = action_generator.pid
            # assert that dices player provided does satisfy the requirement and is legal
            assert (game_state.get_player(pid).get_dices() - player_choice).is_legal()
            assert player_choice.just_satisfy(just(game_state.skill_checker().usable(
                pid, 
                game_state.get_player(pid).just_get_active_character().get_id(),
                action.skill,
            ))[1])
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
        active_character = game_state.get_player(pid).just_get_active_character()
        if not active_character.can_cast_skill():
            return None

        has_castable_skill = any(
            game_state.skill_checker().usable(pid, active_character.get_id(), skill) is not None
            for skill in active_character.skills()
        )
        if not has_castable_skill:
            return None

        return ActionGenerator(
            game_state=game_state,
            pid=pid,
            action=SkillAction._all_none(),
            instruction=DiceOnlyInstruction._all_none(),
            _choices_helper=cls._choices_helper,
            _fill_helper=cls._fill_helper,
        )
