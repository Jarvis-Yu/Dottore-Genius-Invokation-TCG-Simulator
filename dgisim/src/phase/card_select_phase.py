from __future__ import annotations
from typing import Optional, Tuple

import dgisim.src.state.game_state as gm
from dgisim.src.state.player_state import PlayerState
import dgisim.src.phase.phase as ph
from dgisim.src.action import CardSelectAction, Action, EndRoundAction
from dgisim.src.card.cards import Cards
from dgisim.src.helper.level_print import level_print


class CardSelectPhase(ph.Phase):
    _NUM_CARDS: int = 5

    def _draw_cards_and_activate(self, game_state: gm.GameState) -> gm.GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        p1_deck, p1_hand = p1.get_deck_cards().pick_random_cards(self._NUM_CARDS)
        p2_deck, p2_hand = p2.get_deck_cards().pick_random_cards(self._NUM_CARDS)
        new_p1 = p1.factory().phase(
            PlayerState.act.ACTION_PHASE
        ).card_redraw_chances(
            1
        ).deck_cards(
            p1_deck
        ).hand_cards(
            p1_hand
        ).build()
        new_p2 = p2.factory().phase(
            PlayerState.act.ACTION_PHASE
        ).card_redraw_chances(
            1
        ).deck_cards(
            p2_deck
        ).hand_cards(
            p2_hand
        ).build()
        return game_state.factory().player1(new_p1).player2(new_p2).build()

    def _to_starting_hand_select_phase(self, game_state: gm.GameState) -> gm.GameState:
        return game_state.factory().phase(
            game_state.get_mode().starting_hand_select_phase()
        ).player1(
            game_state.get_player1().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        # If both players just entered waiting, assign them cards and make them take actions
        if p1.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            return self._draw_cards_and_activate(game_state)
        elif p1.get_phase() is PlayerState.act.END_PHASE and p2.get_phase() is PlayerState.act.END_PHASE:
            return self._to_starting_hand_select_phase(game_state)
        else:
            raise Exception("Unknown Game State to process")

    def _handle_card_drawing(self, game_state: gm.GameState, pid: gm.GameState.pid, action: CardSelectAction) -> gm.GameState:
        player: PlayerState = game_state.get_player(pid)
        new_deck, new_cards = player.get_deck_cards().pick_random_cards(action.num_cards())
        new_deck = new_deck + action.get_selected_cards()
        new_hand = player.get_hand_cards() - action.get_selected_cards()
        new_hand = new_hand + new_cards
        reducedChances: int = player.get_card_redraw_chances() - 1
        if reducedChances > 0:
            phase: PlayerState.act = player.get_phase()
        else:
            phase: PlayerState.act = PlayerState.act.END_PHASE
        return game_state.factory().player(
            pid,
            player.factory()
            .phase(phase)
            .card_redraw_chances(reducedChances)
            .deck_cards(new_deck)
            .hand_cards(new_hand)
            .build()
        ).build()

    def _handle_end_round(self, game_state: gm.GameState, pid: gm.GameState.pid, action: EndRoundAction) -> gm.GameState:
        player = game_state.get_player(pid)
        return game_state.factory().player(
            pid,
            player.factory()
            .phase(PlayerState.act.END_PHASE)
            .card_redraw_chances(0)
            .build()
        ).build()

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action: Action) -> gm.GameState:
        if isinstance(action, CardSelectAction):
            return self._handle_card_drawing(game_state, pid, action)
        elif isinstance(action, EndRoundAction):
            return self._handle_end_round(game_state, pid, action)
        else:
            raise Exception("Unknown Game State to process")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CardSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
