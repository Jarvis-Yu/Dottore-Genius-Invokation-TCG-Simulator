from __future__ import annotations

import dgisim.src.state.game_state as gm
import dgisim.src.phase.phase as ph
from dgisim.src.state.player_state import PlayerState
from dgisim.src.dices import Dices

class EndPhase(ph.Phase):
    _CARDS_DRAWN = 2

    def _to_roll_phase(self, game_state: gm.GameState, new_round: int) -> gm.GameState:
        active_player_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        active_player_deck, new_cards = active_player.get_deck_cards().pick_random_cards(self._CARDS_DRAWN)
        active_player_hand = active_player.get_hand_cards() + new_cards
        other_player_deck, new_cards = other_player.get_deck_cards().pick_random_cards(self._CARDS_DRAWN)
        other_player_hand = other_player.get_hand_cards() + new_cards
        return game_state.factory().round(
            new_round
        ).phase(
            game_state.get_mode().roll_phase()
        ).player(
            active_player_id,
            game_state.get_player(active_player_id).factory().phase(
                PlayerState.act.PASSIVE_WAIT_PHASE
            ).dices(
                Dices.from_empty()
            ).hand_cards(
                active_player_hand
            ).deck_cards(
                active_player_deck
            ).build()
        ).other_player(
            active_player_id,
            game_state.get_other_player(active_player_id).factory().phase(
                PlayerState.act.PASSIVE_WAIT_PHASE
            ).dices(
                Dices.from_empty()
            ).hand_cards(
                other_player_hand
            ).deck_cards(
                other_player_deck
            ).build()
        ).build()

    def _end_both_players(self, game_state: gm.GameState) -> gm.GameState:
        return game_state.factory().player1(
            game_state.get_player1().factory().phase(
                PlayerState.act.END_PHASE
            ).build()
        ).player2(
            game_state.get_player2().factory().phase(
                PlayerState.act.END_PHASE
            ).build()
        ).build()

    def _end_game(self, game_state: gm.GameState) -> gm.GameState:
        return game_state.factory().phase(
            game_state.get_mode().game_end_phase()
        ).build()

    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        active_player_id = game_state.get_active_player_id()
        if p1.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            return self._end_both_players(game_state)
        elif p1.get_phase() is PlayerState.act.END_PHASE and p2.get_phase() is PlayerState.act.END_PHASE:
            new_round = game_state.get_round() + 1
            if new_round > game_state.get_mode().get_round_limit():
                return self._end_game(game_state)
            else:
                return self._to_roll_phase(game_state, new_round)
        raise Exception("Unknown Game State to process")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EndPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
