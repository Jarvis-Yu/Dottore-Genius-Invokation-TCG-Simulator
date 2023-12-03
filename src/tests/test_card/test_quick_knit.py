import unittest

from .common_imports import *


class TestQuickKnit(unittest.TestCase):
    def test_quick_knit(self):
        base_game_no_summon = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({
                    QuickKnit: 2,
                })
            ).build()
        ).build()

        base_game = base_game_no_summon.factory().f_player1(
            lambda p1: p1.factory().f_summons(
                lambda sms: sms.update_summon(
                    OceanicMimicFrogSummon()
                ).update_summon(
                    BurningFlameSummon()
                )
            ).build()
        ).build()

        # test giving wrong num of dice
        card_action = CardAction(
            card=QuickKnit,
            instruction=StaticTargetInstruction(
                target=StaticTarget(Pid.P1, Zone.SUMMONS, OceanicMimicFrogSummon),
                dice=ActualDice({Element.OMNI: 0}),
            ),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )
        card_action = CardAction(
            card=QuickKnit,
            instruction=StaticTargetInstruction(
                target=StaticTarget(Pid.P1, Zone.SUMMONS, OceanicMimicFrogSummon),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )

        # test invalid summon instruction
        card_action = CardAction(
            card=QuickKnit,
            instruction=StaticTargetInstruction(
                target=StaticTarget(Pid.P1, Zone.SUMMONS, OceanicMimicRaptorSummon),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )

        # test no action generator if no summon
        self.assertIsNone(QuickKnit.action_generator(base_game_no_summon, Pid.P1))

        action_generator = just(QuickKnit.action_generator(base_game, Pid.P1))
        choices = action_generator.choices()
        assert isinstance(choices, tuple)
        self.assertIsInstance(choices[0], StaticTarget)
        action_generator = action_generator.choose(choices[0])
        choices = action_generator.choices()
        assert isinstance(choices, AbstractDice)
        action_generator = action_generator.choose(
            just(action_generator.dice_available().basic_selection(choices))
        )

        # test right usage
        card_action = CardAction(
            card=QuickKnit,
            instruction=StaticTargetInstruction(
                target=StaticTarget(Pid.P1, Zone.SUMMONS, OceanicMimicFrogSummon),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        )
        usages_before = base_game.get_player1().get_summons().just_find(
            OceanicMimicFrogSummon
        ).usages
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)
        usages_after = game_state.get_player1().get_summons().just_find(
            OceanicMimicFrogSummon
        ).usages
        self.assertEqual(usages_before + 1, usages_after)

        card_action = CardAction(
            card=QuickKnit,
            instruction=StaticTargetInstruction(
                target=StaticTarget(Pid.P1, Zone.SUMMONS, BurningFlameSummon),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        )
        usages_before = base_game.get_player1().get_summons().just_find(
            BurningFlameSummon
        ).usages
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        game_state = auto_step(game_state)
        usages_after = game_state.get_player1().get_summons().just_find(
            BurningFlameSummon
        ).usages
        self.assertEqual(usages_before + 1, usages_after)
