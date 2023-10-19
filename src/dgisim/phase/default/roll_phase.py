from __future__ import annotations
from typing import TYPE_CHECKING

from .. import phase as ph

from ...event import RollChancePEvent
from ...action.action import DiceSelectAction, EndRoundAction, PlayerAction
from ...action.action_generator import ActionGenerator
from ...action.enums import ActionType
from ...dice import ActualDice
from ...helper.quality_of_life import just
from ...state.enums import Act, Pid
from ...status.status_processing import StatusProcessing
from ...status.enums import Preprocessables

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...state.game_state import GameState

__all__ = [
    "RollPhase",
]


class RollPhase(ph.Phase):
    _NUM_DICE = 8

    def _get_all_dice_and_activate(self, game_state: GameState) -> GameState:
        base_roll_chances = game_state.get_mode().dice_reroll_chances()
        game_state, p1_chances = StatusProcessing.preprocess_by_all_statuses(
            game_state, Pid.P1, Preprocessables.ROLL_CHANCES,
            RollChancePEvent(pid=Pid.P1, chances=base_roll_chances)
        )
        assert isinstance(p1_chances, RollChancePEvent)
        game_state, p2_chances = StatusProcessing.preprocess_by_all_statuses(
            game_state, Pid.P2, Preprocessables.ROLL_CHANCES,
            RollChancePEvent(pid=Pid.P2, chances=base_roll_chances)
        )
        assert isinstance(p2_chances, RollChancePEvent)
        return game_state.factory().f_player1(
            lambda p1: p1.factory()
            .phase(Act.ACTION_PHASE)
            .dice_reroll_chances(p1_chances.chances)  # type: ignore
            .dice(ActualDice.from_random(RollPhase._NUM_DICE))
            .build()
        ).f_player2(
            lambda p2: p2.factory()
            .phase(Act.ACTION_PHASE)
            .dice_reroll_chances(p2_chances.chances)  # type: ignore
            .dice(ActualDice.from_random(RollPhase._NUM_DICE))
            .build()
        ).build()

    def _to_action_phase(self, game_state: GameState) -> GameState:
        return game_state.factory().f_phase(
            lambda mode: mode.action_phase()
        ).f_player1(
            lambda p1: p1.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        if p1.get_phase().is_passive_wait_phase() and p2.get_phase().is_passive_wait_phase():
            return self._get_all_dice_and_activate(game_state)
        elif p1.get_phase().is_end_phase() and p2.get_phase().is_end_phase():
            return self._to_action_phase(game_state)
        else:
            raise ValueError(f"Given game_state has undefined next state for"
                             + f"{self.__class__.__name__}:\n{game_state}")

    def _handle_dice_selection(
            self,
            game_state: GameState,
            pid: Pid,
            action: DiceSelectAction
    ) -> None | GameState:
        if action.selected_dice.is_empty():
            return self._handle_end_round(game_state, pid)

        player = game_state.get_player(pid)
        dice = player.get_dice()
        kept_dice = dice - action.selected_dice
        assert kept_dice.is_legal()
        replacement_dice = ActualDice.from_random(action.selected_dice.num_dice())
        new_dice = kept_dice + replacement_dice
        new_reroll_chances = player.get_dice_reroll_chances() - 1
        new_player_phase: Act
        if new_reroll_chances > 0:
            new_player_phase = player.get_phase()
        else:
            new_player_phase = Act.END_PHASE
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory()
            .phase(new_player_phase)
            .dice_reroll_chances(new_reroll_chances)
            .dice(new_dice)
            .build()
        ).build()

    def _handle_end_round(
            self,
            game_state: GameState,
            pid: Pid,
    ) -> None | GameState:
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory()
            .phase(Act.END_PHASE)
            .dice_reroll_chances(0)
            .build()
        ).build()

    def step_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: PlayerAction
    ) -> None | GameState:
        if isinstance(action, DiceSelectAction):
            return self._handle_dice_selection(game_state, pid, action)
        else:
            raise ValueError(f"Unknown action {action} provided for game state:\n{game_state}")

    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        return (ActionType.SELECT_DICE, )

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        game_state = action_generator.game_state
        pid = action_generator.pid

        if player_choice is ActionType.SELECT_DICE:
            from ...action.action_generator_generator import DiceSelectionActGenGenerator
            return just(DiceSelectionActGenGenerator.action_generator(game_state, pid))
        else:  # pragma: no cover
            action_type_name = ActionType.__name__
            if isinstance(player_choice, ActionType):
                raise Exception(f"Unhandled player {action_type_name} {player_choice}")
            else:
                raise TypeError(f"Unexpected player choice {player_choice} where"
                                + f"where {action_type_name} is expected")

    def action_generator(self, game_state: GameState, pid: Pid) -> ActionGenerator | None:
        if pid is not self.waiting_for(game_state):
            return None
        return ActionGenerator(
            game_state=game_state,
            pid=pid,
            _choices_helper=self._choices_helper,
            _fill_helper=self._fill_helper,
        )
