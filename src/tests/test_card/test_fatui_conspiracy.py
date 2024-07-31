import unittest
from inspect import isclass
from typing import TypeVar

from .common_imports import *
from src.dgisim.status.status import _FatuiAmbusherStatus

EVENT_CARD = FatuiConspiracy

_FatuiType = TypeVar("_FatuiType", bound=_FatuiAmbusherStatus)


def get_fatuus(game_state: GameState) -> list[_FatuiAmbusherStatus]:
    return [
        combat_status
        for combat_status in game_state.player2.combat_statuses
        if isinstance(combat_status, _FatuiAmbusherStatus)
    ]


def get_fatui(game_state: GameState, fatui: _FatuiType | type[_FatuiType]) -> _FatuiType:
    if not isclass(fatui):
        fatui = type(fatui)  # type: ignore
    return game_state.player2.combat_statuses.just_find(fatui)  # type: ignore


class TestFatuiConspiracy(unittest.TestCase):
    def test_card_in_deck(self):
        self.assertFalse(
            EVENT_CARD.valid_in_deck(
                MutableDeck(chars=[Tartaglia, Nahida, RaidenShogun], cards={})
            )
        )
        self.assertTrue(
            EVENT_CARD.valid_in_deck(
                MutableDeck(chars=[Tartaglia, FatuiPyroAgent, RaidenShogun], cards={})
            )
        )

    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({EVENT_CARD: 2}))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({LightningStiletto: 1}))
        base_state = add_dmg_listener(base_state, Pid.P2)
        base_state = add_aura_remover(base_state, Pid.P1)
        base_state = add_aura_remover(base_state, Pid.P2)

        assert isinstance(p2_chars(base_state)[2], Keqing)

        """ check status dmg post skill """
        game_state = base_state
        # playing the cards adds a fatui status to the opponent
        game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=2)
        oppo_fatuus = get_fatuus(game_state)
        self.assertEqual(len(oppo_fatuus), 1)
        first_fatui = oppo_fatuus[0]
        self.assertEqual(first_fatui.usages, 2)

        # self skill doesn't trigger fatui
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P2)), 0)
        self.assertEqual(get_fatui(game_state, first_fatui).usages, 2)

        # oppo skill trigger fatui
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P2, last_index=1, source=StaticTarget.from_player_active(game_state, Pid.P2))
        assert_last_dmg(self, game_state, Pid.P2, last_index=0, amount=1, elem=first_fatui.ELEMENT)
        first_fatui = get_fatui(game_state, first_fatui)
        self.assertEqual(get_fatui(game_state, first_fatui).usages, 1)

        # oppo swap doesn't trigger
        game_state = end_round(game_state, Pid.P1)
        game_state = step_swap(game_state, Pid.P2, 2)
        first_fatui = get_fatui(game_state, first_fatui)
        self.assertEqual(get_fatui(game_state, first_fatui).usages, 1)

        # oppo card skill triggers
        game_state = play_dice_only_card(game_state, Pid.P2, LightningStiletto)
        assert_last_dmg(
            self, game_state, Pid.P2, last_index=1,
            source=StaticTarget.from_player_active(game_state, Pid.P2), elem=Element.ELECTRO,
        )
        assert_last_dmg(self, game_state, Pid.P2, last_index=0, amount=1, elem=first_fatui.ELEMENT)
        self.assertNotIn(type(first_fatui), game_state.player2.combat_statuses)

        """ check generated fatuus doens't try to be different """
        for _ in range(5):
            game_state = base_state
            game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=2)
            game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=2)
            fatuus = get_fatuus(game_state)
            self.assertTrue(len(fatuus) == 1 or len(fatuus) == 2)
            self.assertEqual(
                len(fatuus),
                len(set([type(fatui) for fatui in fatuus])),
            )

        """ check the fatuus cannot be boosted """
        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, EVENT_CARD, cost=2)
        oppo_fatuus = get_fatuus(game_state)
        first_fatui = oppo_fatuus[0]
        game_state = end_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertTrue(dmg.damage_type.no_boost)
