import unittest

from .common_imports import *

class TestTimaeus(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Timaeus: 2,
            GamblersEarrings: 2,
            InstructorsCap: 2,
            TenacityOfTheMillelith: 2,
        }))

        # test Timaeus cannot discount if it cannot make it free
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Timaeus,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        timaeus_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(timaeus_support, TimaeusSupport)
        self.assertEqual(timaeus_support.usages, 2)
        self.assertFalse(timaeus_support.used)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TenacityOfTheMillelith,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))
        
        # test Timaeus can discount if it can make it free
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty()
            ),
        ))
        timaeus_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(timaeus_support, TimaeusSupport)
        self.assertEqual(timaeus_support.usages, 1)
        self.assertTrue(timaeus_support.used)

        # test Cost deduction only once per round
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        timaeus_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(timaeus_support, TimaeusSupport)
        self.assertEqual(timaeus_support.usages, 1)
        self.assertTrue(timaeus_support.used)

        # check that usages increases and used resets every round
        game_state = next_round(game_state)
        timaeus_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(timaeus_support, TimaeusSupport)
        self.assertEqual(timaeus_support.usages, 2)
        self.assertFalse(timaeus_support.used)

    def test_priority_with_yayoi_nanatsuki(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            InstructorsCap: 2,
        }))
        base_state = AddSupportEffect(Pid.P1, TimaeusSupport).execute(base_state)
        base_state = AddSupportEffect(Pid.P1, YayoiNanatsukiSupport).execute(base_state)

        game_state = base_state

        # check Yayoi Nanatsuki's discount is applied first
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=InstructorsCap,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        yayoi_support = game_state.player1.supports.just_find_by_sid(2)
        timaeus_support = game_state.player1.supports.just_find_by_sid(1)
        assert isinstance(yayoi_support, YayoiNanatsukiSupport)
        assert isinstance(timaeus_support, TimaeusSupport)
        self.assertEqual(yayoi_support.usages, 0)
        self.assertEqual(timaeus_support.usages, 1)
        self.assertTrue(timaeus_support.used)

    def test_draw_on_play(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Timaeus: 1,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            GamblersEarrings: 3,
        }))
        base_state = replace_init_deck(base_state, Pid.P1, Cards({
            InstructorsCap: 2,
            GamblersEarrings: 3,
        }))

        # test play with less than 6 artifacts in initial deck doesn't draw
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Timaeus,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({}),
        )

        # test play with 6 artifacts in initial deck draws 1
        game_state = base_state
        game_state = replace_init_deck(game_state, Pid.P1, Cards({
            InstructorsCap: 2,
            GamblersEarrings: 2,
            GeneralsAncientHelm: 1,
            GildedDreams: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Timaeus,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({GamblersEarrings: 1}),
        )
