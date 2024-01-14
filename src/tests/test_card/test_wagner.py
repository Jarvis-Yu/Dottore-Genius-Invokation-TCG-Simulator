import unittest

from .common_imports import *

class TestWagner(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Wagner: 2,
            TravelersHandySword: 2,
            AquilaFavonia: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)

        # test Wagner cannot discount if it cannot make it free
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Wagner,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        wagner_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(wagner_support, WagnerSupport)
        self.assertEqual(wagner_support.usages, 2)
        self.assertFalse(wagner_support.used)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AquilaFavonia,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))
        
        # test Wagner can discount if it can make it free
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty()
            ),
        ))
        wagner_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(wagner_support, WagnerSupport)
        self.assertEqual(wagner_support.usages, 0)
        self.assertTrue(wagner_support.used)

        # test Cost deduction only once per round
        game_state = UpdateSupportEffect(
            target_pid=Pid.P1,
            support=replace(wagner_support, usages=2)
        ).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        wagner_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(wagner_support, WagnerSupport)
        self.assertEqual(wagner_support.usages, 2)
        self.assertTrue(wagner_support.used)

        # check that usages increases and used resets every round
        game_state = next_round(game_state)
        wagner_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(wagner_support, WagnerSupport)
        self.assertEqual(wagner_support.usages, 3)
        self.assertFalse(wagner_support.used)

    def test_priority_with_master_zhang(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TravelersHandySword: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = AddSupportEffect(Pid.P1, WagnerSupport).execute(base_state)
        base_state = AddSupportEffect(Pid.P1, MasterZhangSupport).execute(base_state)

        game_state = base_state

        # check Master Zhang's discount is applied first
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        zhang_support = game_state.player1.supports.just_find_by_sid(2)
        wagner_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(zhang_support, MasterZhangSupport)
        assert isinstance(wagner_support, WagnerSupport)
        self.assertEqual(zhang_support.usages, 0)
        self.assertEqual(wagner_support.usages, 1)
        self.assertTrue(wagner_support.used)

    def test_draw_on_play(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Wagner: 1,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            AquilaFavonia: 3,
        }))
        base_state = replace_init_deck(base_state, Pid.P1, Cards({
            WolfsGravestone: 1,
            TheBell: 2,
        }))

        # test play with less than 3 kinds of weapons in initial deck doesn't draw
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Wagner,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({}),
        )

        # test play with 3 kinds of weapons in initial deck draws 1
        game_state = base_state
        game_state = replace_init_deck(game_state, Pid.P1, Cards({
            WolfsGravestone: 1,
            TheBell: 1,
            KingsSquire: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Wagner,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({AquilaFavonia: 1}),
        )
