import unittest

from .common_imports import *

class TestSetaria(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().hand_cards(Cards({
                Setaria: 2,
            })).deck_cards(Cards({
                IHaventLostYet: 6,
            })).build()
        ).build()

        # post card play
        game_state = base_state
        for _ in range(2):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=Setaria,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1}))
            ))
        sups = game_state.player1.supports
        hands = game_state.player1.hand_cards
        set1, set2 = sups.just_find(SetariaSupport, 1), sups.just_find(SetariaSupport, 2)
        assert isinstance(set1, SetariaSupport) and isinstance(set2, SetariaSupport)
        self.assertEqual(set1.usages, 2)
        self.assertEqual(set2.usages, 3)
        self.assertEqual(hands[IHaventLostYet], 1)

        # post skill destroy card
        game_state = replace_character_make_active_add_card(
            game_state, Pid.P1, Keqing, 2, LightningStiletto,
        )
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({LightningStiletto: 1}))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        sups = game_state.player1.supports
        hands = game_state.player1.hand_cards
        set1, set2 = sups.just_find(SetariaSupport, 1), sups.just_find(SetariaSupport, 2)
        assert isinstance(set1, SetariaSupport) and isinstance(set2, SetariaSupport)
        self.assertEqual(set1.usages, 1)
        self.assertEqual(set2.usages, 3)
        self.assertEqual(hands[IHaventLostYet], 1)

        # post tuning
        game_state = step_action(game_state, Pid.P1, ElementalTuningAction(
            card=IHaventLostYet,
            dice_elem=Element.ANEMO,
        ))
        sups = game_state.player1.supports
        hands = game_state.player1.hand_cards
        set1, set2 = sups.find(SetariaSupport, 1), sups.just_find(SetariaSupport, 2)  # type: ignore
        assert set1 is None and isinstance(set2, SetariaSupport)
        self.assertEqual(set2.usages, 3)
        self.assertEqual(hands[IHaventLostYet], 1)