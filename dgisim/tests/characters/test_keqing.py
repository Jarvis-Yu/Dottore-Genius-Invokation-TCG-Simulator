import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.agents import PuppetAgent
from dgisim.src.action import *
from dgisim.src.character.character import Keqing
from dgisim.src.card.card import *
from dgisim.src.status.status import *


class TestKeqing(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(3).build()
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(PlayerState.Act.END_PHASE).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Keqing

    def testKeqingNormalAttack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            CharacterSkill.NORMAL_ATTACK,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().elem_auras())

    def testKeqingElementalSkill(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            CharacterSkill.ELEMENTAL_SKILL1,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        p2ac = gsm.get_game_state().get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)

        # first skill
        gsm.player_step()
        gsm.auto_step()
        game_state_1 = gsm.get_game_state()  # after first skill cast
        p2ac = game_state_1.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertTrue(game_state_1.get_player1().get_hand_cards().contains(LightningStiletto))

        # reset opponenet
        game_state_1 = game_state_1.factory().player2(
            self.BASE_GAME.get_player2()
        ).build()

        # second skill by casting skill directly
        gsm = GameStateMachine(game_state_1, a1, a2)
        a1.inject_action(SkillAction(
            CharacterSkill.ELEMENTAL_SKILL1,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state_1_1 = gsm.get_game_state()
        p2ac = game_state_1_1.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(game_state_1_1.get_player1().get_hand_cards().contains(LightningStiletto))

        # second skill by using card, when Keqing on field
        source = StaticTarget(GameState.Pid.P1, Zone.CHARACTER, 3)
        gsm = GameStateMachine(game_state_1, a1, a2)
        a1.inject_action(CardAction(
            LightningStiletto,
            CharacterTargetInstruction(
                dices=ActualDices({}),
                target=source,
            )
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state_1_2 = gsm.get_game_state()
        p2ac = game_state_1_2.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(game_state_1_2.get_player1().get_hand_cards().contains(LightningStiletto))

        # second skill by using card, when Keqing off field
        game_state = game_state_1.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(1).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(CardAction(
            LightningStiletto,
            CharacterTargetInstruction(
                dices=ActualDices({}),
                target=source,
            )
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state_1_2 = gsm.get_game_state()
        p2ac = game_state_1_2.get_player2().just_get_active_character()
        p1ac = game_state_1_2.get_player1().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(game_state_1_2.get_player1().get_hand_cards().contains(LightningStiletto))
        self.assertEqual(type(p1ac), Keqing)

        # reset p2
        game_state_1_2 = game_state_1_2.factory().player2(
            self.BASE_GAME.get_player2()
        ).build()

        # test normal attack electro infused
        gsm = GameStateMachine(game_state_1_2, a1, a2)
        a1.inject_action(SkillAction(
            CharacterSkill.NORMAL_ATTACK,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.player_step()
        gsm.auto_step()
        game_state_infused = gsm.get_game_state()
        p2ac = game_state_infused.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertTrue(p2ac.get_elemental_aura().contains(Element.ELECTRO))
        self.assertFalse(game_state_infused.get_player1(
        ).get_hand_cards().contains(LightningStiletto))

        # test ElectroInfusion disappear when two round ends
        gsm = GameStateMachine(game_state_infused, a1, a2)
        a1.inject_actions([
            EndRoundAction(),
            EndRoundAction(),
            EndRoundAction(),
        ])
        a2.inject_actions([
            EndRoundAction(),
            EndRoundAction(),
            EndRoundAction(),
        ])
        # initially
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertEqual(
            p1ac.get_character_statuses().just_find(ElectroInfusionStatus).duration,
            2
        )
        # next round
        gsm.step_until_phase(game_state.get_mode().end_phase())
        gsm.step_until_phase(game_state.get_mode().action_phase())
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertEqual(
            p1ac.get_character_statuses().just_find(ElectroInfusionStatus).duration,
            1
        )
        # next round
        gsm.step_until_phase(game_state.get_mode().end_phase())
        gsm.step_until_phase(game_state.get_mode().action_phase())
        p1ac = gsm.get_game_state().get_player1().just_get_active_character()
        self.assertFalse(p1ac.get_character_statuses().contains(ElectroInfusionStatus))
