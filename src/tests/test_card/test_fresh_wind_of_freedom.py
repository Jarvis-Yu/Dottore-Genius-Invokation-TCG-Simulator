import unittest

from .common_imports import *


class TestFreshWindOfFreedom(unittest.TestCase):
    def test_wind_and_freedom_kill(self):
        base_game = PublicAddCardEffect(Pid.P1, card=FreshWindOfFreedom).execute(ACTION_TEMPLATE)
        game_state = kill_character(base_game, 1, hp=1)
        a1, a2 = PuppetAgent(), LazyAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_actions([
            CardAction(
                card=FreshWindOfFreedom,
                instruction=DiceOnlyInstruction(dice=ActualDice.from_empty())
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
            ),
            SkillAction(
                skill=CharacterSkill.SKILL1,
                instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3}))
            ),
        ])
        gsm.player_step(); gsm.auto_step()  # P1 play card
        gsm.player_step(); gsm.auto_step()  # P1 normal attack
        self.assertTrue(gsm.get_game_state().death_swapping())
        gsm.player_step(); gsm.auto_step()  # P2 death swap
        game_state = gsm.get_game_state()
        self.assertEqual(gsm.get_game_state().get_active_player_id(), Pid.P1)
        self.assertNotIn(FreshWindOfFreedomStatus, game_state.get_player1().get_combat_statuses())
        gsm.player_step(); gsm.auto_step()  # P1 normal attack
        self.assertEqual(gsm.get_game_state().get_active_player_id(), Pid.P2)

    def test_wind_and_freedom_disappear(self):
        base_game = PublicAddCardEffect(Pid.P1, card=FreshWindOfFreedom).execute(ACTION_TEMPLATE)
        game_state = kill_character(base_game, 1, Pid.P1, hp=1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FreshWindOfFreedom,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P1, DeathSwapAction(char_id=2))
        self.assertIn(FreshWindOfFreedomStatus, game_state.get_player1().get_combat_statuses())
        self.assertEqual(game_state.get_active_player_id(), Pid.P1)
        a1, a2 = LazyAgent(), LazyAgent()
        gsm = GameStateMachine(game_state, a1, a2)
        gsm.step_until_next_phase()
        gsm.step_until_phase(game_state.get_mode().action_phase)
        game_state = gsm.get_game_state()
        self.assertNotIn(FreshWindOfFreedomStatus, game_state.get_player1().get_combat_statuses())

    def test_as_arcane_legend(self):
        base_game = PublicAddCardEffect(Pid.P1, card=FreshWindOfFreedom).execute(ACTION_TEMPLATE)
        base_game = PublicAddCardEffect(Pid.P1, card=FreshWindOfFreedom).execute(base_game)
        
        game_state = step_action(base_game, Pid.P1, CardAction(
            card=FreshWindOfFreedom,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        # a second Arcane Legend Card cannot be used afterwards
        self.assertRaises(Exception, lambda: step_action(game_state, Pid.P1, CardAction(
            card=FreshWindOfFreedom,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        )))