import unittest

from .common_imports import *

class TestDunyarzad(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TreasureSeekingSeelie: 1,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            LeaveItToMe: 5,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)

        # test any skill counts (except opponent's)
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TreasureSeekingSeelie,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        seelie_support = game_state.player1.supports.just_find_by_sid(1)
        self.assertIsInstance(seelie_support, TreasureSeekingSeelieSupport)
        assert isinstance(seelie_support, TreasureSeekingSeelieSupport)
        self.assertEqual(seelie_support.usages, 0)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        seelie_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(seelie_support, TreasureSeekingSeelieSupport)
        self.assertEqual(seelie_support.usages, 1)

        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        seelie_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(seelie_support, TreasureSeekingSeelieSupport)
        self.assertEqual(seelie_support.usages, 1)

        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        seelie_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(seelie_support, TreasureSeekingSeelieSupport)
        self.assertEqual(seelie_support.usages, 2)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 0)

        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertNotIn(TreasureSeekingSeelieSupport, game_state.player1.supports)
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({LeaveItToMe: 3}),
        )
