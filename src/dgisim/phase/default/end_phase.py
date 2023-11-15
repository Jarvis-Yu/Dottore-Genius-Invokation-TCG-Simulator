from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .. import phase as ph

from ...action.action import *
from ...action.action_generator import ActionGenerator
from ...dice import ActualDice
from ...effect.effect import *
from ...effect.enums import Zone
from ...effect.structs import StaticTarget
from ...state.enums import Pid, Act

if TYPE_CHECKING:
    from ...action.types import DecidedChoiceType, GivenChoiceType
    from ...state.game_state import GameState


__all__ = [
    "EndPhase",
]


class EndPhase(ph.Phase):
    def _initialize_end_phase(self, game_state: GameState) -> GameState:
        active_pid = game_state.get_active_player_id()
        effects: list[Effect] = []
        effects += [
            EndPhaseCheckoutEffect(),
            EndRoundEffect(),
            SetBothPlayerPhaseEffect(Act.END_PHASE),
        ]
        return game_state.factory().f_effect_stack(
            lambda es: es.push_many_fl(effects)
        ).f_player(
            active_pid,
            lambda p: p.factory().phase(Act.ACTIVE_WAIT_PHASE).build()
        ).build()

    def _to_roll_phase(self, game_state: GameState, new_round: int) -> GameState:
        active_player_id = game_state.get_active_player_id()
        active_player = game_state.get_player(active_player_id)
        other_player = game_state.get_other_player(active_player_id)
        cards_per_round = game_state.get_mode().cards_per_round()
        hand_card_limit = game_state.get_mode().hand_card_limit()
        active_player_deck, new_cards = (
            active_player.get_deck_cards().pick_random_cards(cards_per_round)
        )
        active_player_hand = active_player.get_hand_cards().extend(new_cards, limit=hand_card_limit)
        other_player_deck, new_cards = (
            other_player.get_deck_cards().pick_random_cards(cards_per_round)
        )
        other_player_hand = other_player.get_hand_cards().extend(new_cards, limit=hand_card_limit)
        return game_state.factory().round(
            new_round
        ).phase(
            game_state.get_mode().roll_phase()
        ).f_player(
            active_player_id,
            lambda p: p.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).dice(
                ActualDice.from_empty()
            ).hand_cards(
                active_player_hand
            ).deck_cards(
                active_player_deck
            ).build()
        ).f_other_player(
            active_player_id,
            lambda p: p.factory().phase(
                Act.PASSIVE_WAIT_PHASE
            ).dice(
                ActualDice.from_empty()
            ).hand_cards(
                other_player_hand
            ).deck_cards(
                other_player_deck
            ).build()
        ).build()

    def _end_game(self, game_state: GameState) -> GameState:
        return game_state.factory().phase(
            game_state.get_mode().game_end_phase()
        ).build()

    def _execute_effect(self, game_state: GameState) -> GameState:
        effect_stack, effect = game_state.get_effect_stack().pop()
        new_game_state = game_state.factory().effect_stack(effect_stack).build()
        if isinstance(effect, DeathSwapPhaseStartEffect):
            raise Exception("Not Reached!")
        return effect.execute(new_game_state)

    def _is_executing_effects(self, game_state: GameState) -> bool:
        effect_stack = game_state.get_effect_stack()
        return not effect_stack.is_empty() \
            and not isinstance(effect_stack.peek(), DeathSwapPhaseStartEffect)

    def step(self, game_state: GameState) -> GameState:
        p1 = game_state.get_player1()
        p2 = game_state.get_player2()
        active_player_id = game_state.get_active_player_id()
        if p1.in_passive_wait_phase() and p2.in_passive_wait_phase():
            return self._initialize_end_phase(game_state)
        elif p1.in_active_wait_phase() or p2.in_active_wait_phase():
            assert self._is_executing_effects(game_state)
            return self._execute_effect(game_state)
        elif p1.in_action_phase() or p2.in_action_phase():
            # handling death swap
            assert self._is_executing_effects(game_state)
            return self._execute_effect(game_state)
        elif p1.in_end_phase() and p2.in_end_phase():
            new_round = game_state.get_round() + 1
            if new_round > game_state.get_mode().round_limit():
                return self._end_game(game_state)
            else:
                return self._to_roll_phase(game_state, new_round)
        raise Exception("Unknown Game State to process")  # pragma: no cover

    def _handle_death_swap_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: DeathSwapAction
    ) -> Optional[GameState]:
        player = game_state.get_player(pid)
        effect_stack = game_state.get_effect_stack()
        # Add Effects
        active_character = player.get_characters().get_active_character()
        assert active_character is not None
        effect_stack = effect_stack.push_one(SwapCharacterEffect(
            StaticTarget(pid, Zone.CHARACTERS, action.char_id)
        ))
        return game_state.factory().effect_stack(
            effect_stack
        ).build()

    def step_action(
            self,
            game_state: GameState,
            pid: Pid,
            action: PlayerAction
    ) -> Optional[GameState]:
        effect_stack = game_state.get_effect_stack()
        if (effect_stack.is_not_empty()
                and isinstance(effect_stack.peek(), DeathSwapPhaseStartEffect)):
            game_state = game_state.factory().effect_stack(effect_stack.pop()[0]).build()
        if isinstance(action, DeathSwapAction):
            return self._handle_death_swap_action(game_state, pid, action)

        raise NotImplementedError

    def waiting_for(self, game_state: GameState) -> Optional[Pid]:
        effect_stack = game_state.get_effect_stack()
        # if no effects are to be executed or death swap phase is inserted
        if effect_stack.is_not_empty() \
                and isinstance(effect_stack.peek(), DeathSwapPhaseStartEffect):
            return super().waiting_for(game_state)
        else:
            return None

    def action_generator(self, game_state: GameState, pid: Pid) -> ActionGenerator | None:
        if pid is not self.waiting_for(game_state):  # pragma: no cover
            return None
        assert game_state.death_swapping(pid)
        from ...action.action_generator_generator import SwapActGenGenerator
        return SwapActGenGenerator.action_generator(game_state, pid)
