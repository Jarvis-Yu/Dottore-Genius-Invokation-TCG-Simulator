import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.card.cards import *
from dgisim.src.card.card import *
from dgisim.src.status.status import *
from dgisim.src.support.support import *
from dgisim.src.agents import *


class TestLotusFlowerCrisps(unittest.TestCase):
    def testCardNormalUsage(self):
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
            lambda: base_game.action_step(GameState.Pid.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=LotusFlowerCrisp,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.OMNI: 1}),
                target=StaticTarget(
                    pid=GameState.Pid.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(GameState.Pid.P1, card_action)
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
        low_health_game_state = kill_character(buffed_game_state, 1, pid=GameState.Pid.P1, hp=5)
        game_state = add_damage_effect(
            low_health_game_state,
            4,
            Element.PYRO,
            pid=GameState.Pid.P1,
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
            pid=GameState.Pid.P1,
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
        a1.inject_action(EndRoundAction())
        a2.inject_action(EndRoundAction())
        gsm.step_until_next_phase()
        gsm.step_until_phase(low_health_game_state.get_mode().action_phase())
        game_state = gsm.get_game_state()
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIsNone(p1ac.get_character_statuses().find(LotusFlowerCrispStatus))
