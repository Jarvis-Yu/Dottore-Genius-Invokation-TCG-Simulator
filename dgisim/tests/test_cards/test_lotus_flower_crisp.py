import unittest

from dgisim.tests.test_cards.common_imports import *


class TestLotusFlowerCrisps(unittest.TestCase):
    def test_card_normal_usage(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({LotusFlowerCrisp: 2})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=LotusFlowerCrisp,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(PID.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=LotusFlowerCrisp,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.OMNI: 1}),
                target=StaticTarget(
                    pid=PID.P1,
                    zone=ZONE.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(PID.P1, card_action)
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
        low_health_game_state = kill_character(buffed_game_state, 1, pid=PID.P1, hp=5)
        game_state = add_damage_effect(
            low_health_game_state,
            4,
            Element.PYRO,
            pid=PID.P1,
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
            pid=PID.P1,
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
        a1.inject_action(EndRoundAction()) # skip roll phase
        a2.inject_action(EndRoundAction())
        gsm.step_until_next_phase()
        gsm.step_until_phase(low_health_game_state.get_mode().action_phase())
        game_state = gsm.get_game_state()
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIsNone(p1ac.get_character_statuses().find(LotusFlowerCrispStatus))
