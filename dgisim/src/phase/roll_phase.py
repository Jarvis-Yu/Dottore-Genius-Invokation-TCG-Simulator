from __future__ import annotations

import dgisim.src.phase.phase as ph
import dgisim.src.state.game_state as gm
from dgisim.src.dices import Dices
from dgisim.src.element.element import Element
from dgisim.src.state.player_state import PlayerState


class RollPhase(ph.Phase):
    _NUM_DICES = 8

    def step(self, game_state: gm.GameState) -> gm.GameState:
        # if game_state.get_active_player().is_player1():
        #     p1_phase = PlayerState.act.ACTIVE_WAIT_PHASE
        #     p2_phase = PlayerState.act.PASSIVE_WAIT_PHASE
        # elif game_state.get_active_player().is_player2():
        #     p1_phase = PlayerState.act.PASSIVE_WAIT_PHASE
        #     p2_phase = PlayerState.act.ACTIVE_WAIT_PHASE
        # else:
        #     raise Exception("Undefined Player id")
        return game_state.factory().phase(
            game_state.get_mode().action_phase()
        ).player1(
            game_state.get_player1().factory()
            .phase(PlayerState.act.PASSIVE_WAIT_PHASE)
            .dices(Dices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            .build()
        ).player2(
            game_state.get_player2().factory()
            .phase(PlayerState.act.PASSIVE_WAIT_PHASE)
            .dices(Dices.from_all(RollPhase._NUM_DICES, Element.OMNI))
            .build()
        ).build()
    """
    def step(self, game_state: gm.GameState) -> gm.GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        # If both players just entered waiting, assign them cards and make them take actions
        if p1.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE and p2.get_phase() is PlayerState.act.PASSIVE_WAIT_PHASE:
            new_p1, new_p2 = self._assign_cards_and_inform_action(p1, p2)
            return game_state.factory().player1(new_p1).player2(new_p2).build()
        # Otherwise move to the next game phase making both players wait
        assert p1.get_phase() is PlayerState.act.END_PHASE and p2.get_phase() is PlayerState.act.END_PHASE
        return game_state.factory().phase(
            game_state.get_mode().starting_hand_select_phase()
        ).player1(
            game_state.get_player1().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).player2(
            game_state.get_player2().factory().phase(PlayerState.act.PASSIVE_WAIT_PHASE).build()
        ).build()

    def step_action(self, game_state: gm.GameState, pid: gm.GameState.pid, action: Action) -> gm.GameState:
        assert isinstance(action, CardSelectAction)
        card_action: CardSelectAction = action
        player: PlayerState = game_state.get_player(pid)
        new_deck, new_cards = player.get_deck_cards().pick_random_cards(card_action.num_cards())
        new_deck = new_deck + card_action.get_selected_cards()
        new_hand = player.get_hand_cards() - card_action.get_selected_cards()
        new_hand = new_hand + new_cards
        reducedChances: int = player.get_card_redraw_chances() - 1
        if reducedChances > 0:
            phase: PlayerState.act = player.get_phase()
        else:
            phase: PlayerState.act = PlayerState.act.END_PHASE
        return game_state.factory().player(
            pid,
            player.factory()
            .card_redraw_chances(reducedChances)
            .phase(phase)
            .deck_cards(new_deck)
            .hand_cards(new_hand)
            .build()
        ).build()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CardSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
    """
