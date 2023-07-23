from __future__ import annotations
from dataclasses import replace
from typing import Optional, TYPE_CHECKING

from .. import phase as ph

from ...action.action import CardsSelectAction, PlayerAction, EndRoundAction
from ...action.action_generator import ActionGenerator
from ...action.enums import ActionType
from ...helper.quality_of_life import just
from ...state.enums import Pid, Act

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...state.game_state import GameState
    from ...state.player_state import PlayerState

__all__ = [
    "CardSelectPhase",
]


class CardSelectPhase(ph.Phase):
    _NUM_CARDS: int = 5

    def _draw_cards_and_activate(self, game_state: GameState) -> GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        p1_deck, p1_hand = p1.get_deck_cards().pick_random_cards(self._NUM_CARDS)
        p2_deck, p2_hand = p2.get_deck_cards().pick_random_cards(self._NUM_CARDS)
        mode = game_state.get_mode()
        return game_state.factory().f_player1(
            lambda p1: p1.factory()
            .phase(Act.ACTION_PHASE)
            .card_redraw_chances(game_state.get_mode().card_redraw_chances())
            .deck_cards(p1_deck)
            .hand_cards(p1_hand)
            .build()
        ).f_player2(
            lambda p2: p2.factory()
            .phase(Act.ACTION_PHASE)
            .card_redraw_chances(game_state.get_mode().card_redraw_chances())
            .deck_cards(p2_deck)
            .hand_cards(p2_hand)
            .build()
        ).build()

    def _to_starting_hand_select_phase(self, game_state: GameState) -> GameState:
        return game_state.factory().f_phase(
            lambda mode: mode.starting_hand_select_phase()
        ).f_player1(
            lambda p1: p1.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).f_player2(
            lambda p2: p2.factory().phase(Act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: GameState) -> GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        # If both players just entered waiting, assign them cards and make them take actions
        if p1.get_phase() is Act.PASSIVE_WAIT_PHASE and p2.get_phase() is Act.PASSIVE_WAIT_PHASE:
            return self._draw_cards_and_activate(game_state)
        elif p1.get_phase() is Act.END_PHASE and p2.get_phase() is Act.END_PHASE:
            return self._to_starting_hand_select_phase(game_state)
        else:
            raise Exception("Unknown Game State to process")

    def _handle_card_drawing(self, game_state: GameState, pid: Pid, action: CardsSelectAction) -> GameState:
        player: PlayerState = game_state.get_player(pid)
        new_deck, new_cards = player.get_deck_cards().pick_random_cards(action.selected_cards.num_cards())
        new_deck = new_deck + action.selected_cards
        new_hand = player.get_hand_cards() - action.selected_cards
        new_hand = new_hand + new_cards
        new_redraw_chances: int = player.get_card_redraw_chances() - 1
        new_player_phase: Act
        if new_redraw_chances > 0:
            new_player_phase = player.get_phase()
        else:
            new_player_phase = Act.END_PHASE
        return game_state.factory().player(
            pid,
            player.factory()
            .phase(new_player_phase)
            .card_redraw_chances(new_redraw_chances)
            .deck_cards(new_deck)
            .hand_cards(new_hand)
            .build()
        ).build()

    def _handle_end_round(
            self,
            game_state: GameState,
            pid: Pid,
            action: EndRoundAction
    ) -> GameState:
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory()
            .phase(Act.END_PHASE)
            .card_redraw_chances(0)
            .build()
        ).build()

    def step_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: PlayerAction
    ) -> Optional[GameState]:
        if isinstance(action, CardsSelectAction):
            return self._handle_card_drawing(game_state, pid, action)
        elif isinstance(action, EndRoundAction):
            return self._handle_end_round(game_state, pid, action)
        else:
            raise ValueError(f"Unknown action {action} provided for game state:\n{game_state}")

    @classmethod
    def _choices_helper(cls, action_generator: ActionGenerator) -> GivenChoiceType:
        return (ActionType.SELECT_CARDS, ActionType.END_ROUND)

    @classmethod
    def _fill_helper(
        cls,
        action_generator: ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> ActionGenerator:
        game_state = action_generator.game_state
        pid = action_generator.pid

        if player_choice is ActionType.SELECT_CARDS:
            from ...action.action_generator_generator import CardsSelectionActGenGenerator
            return just(CardsSelectionActGenGenerator.action_generator(game_state, pid))
        elif player_choice is ActionType.END_ROUND:
            return ActionGenerator(game_state=game_state, pid=pid, action=EndRoundAction())
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
