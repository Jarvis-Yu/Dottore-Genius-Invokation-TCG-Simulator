import unittest

from src.tests.test_card.common_imports import *


class TestLotusFlowerCrisps(unittest.TestCase):
    def test_card_normal_usage(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({LotusFlowerCrisp: 2})
            ).build()
        ).build()

        # test giving wrong num of dice
        card_action = CardAction(
            card=LotusFlowerCrisp,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(Pid.P1, card_action)
        )

        # test giving right num of dice
        card_action = CardAction(
            card=LotusFlowerCrisp,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 1}),
                target=StaticTarget(
                    pid=Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(Pid.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertEqual(
            buffed_game_state
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .just_find(LotusFlowerCrispStatus)
            .usages,
            1
        )
        self.assertTrue(
            buffed_game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test when shield takes 4 damage
        low_health_game_state = kill_character(buffed_game_state, 1, pid=Pid.P1, hp=5)
        game_state = add_damage_effect(
            low_health_game_state,
            4,
            Element.PYRO,
            pid=Pid.P1,
            char_id=1,
        )
        game_state = auto_step(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 4)
        self.assertTrue(p1ac.get_elemental_aura().contains(Element.PYRO))
        self.assertIsNone(p1ac.get_character_statuses().find(LotusFlowerCrispStatus))

        # test when shield takes 2 damage
        game_state = add_damage_effect(
            low_health_game_state,
            2,
            Element.PYRO,
            pid=Pid.P1,
            char_id=1,
        )
        game_state = auto_step(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_hp(), 5)
        self.assertTrue(p1ac.get_elemental_aura().contains(Element.PYRO))
        self.assertIsNone(p1ac.get_character_statuses().find(LotusFlowerCrispStatus))

        # test shield disappears after round ends
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(low_health_game_state, a1, a2)
        # End Action Phase
        a1.inject_action(EndRoundAction()) # skip action phase
        a2.inject_action(EndRoundAction())
        a1.inject_action(DiceSelectAction(selected_dice=ActualDice({}))) # skip roll phase
        a2.inject_action(DiceSelectAction(selected_dice=ActualDice({})))
        gsm.step_until_next_phase()
        gsm.step_until_phase(low_health_game_state.get_mode().action_phase())
        game_state = gsm.get_game_state()
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIsNone(p1ac.get_character_statuses().find(LotusFlowerCrispStatus))
