import unittest

from src.tests.test_characters.common_imports import *


class TestBennett(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Bennett.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(GrandExpectation)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Bennett

    def test_normal_attack(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL1,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.elem_auras())

    def test_elemental_skill1(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        gsm = GameStateMachine(self.BASE_GAME, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.SKILL2,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)

    def test_elemental_burst(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = fill_energy_for_all(self.BASE_GAME)
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(SkillAction(
            skill=CharacterSkill.ELEMENTAL_BURST,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4})),
        ))
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)

        gsm.player_step()
        gsm.auto_step()
        p1 = gsm.get_game_state().player1
        p2ac = gsm.get_game_state().player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(InspirationFieldStatus, p1.combat_statuses)
        burst_status = p1.combat_statuses.just_find(InspirationFieldStatus)
        self.assertEqual(burst_status.usages, 2)
        self.assertEqual(burst_status.activated, False)

    def test_talent_card(self):
        base_game = fill_energy_for_all(self.BASE_GAME)
        base_game = kill_character(base_game, character_id=2, pid=Pid.P1, hp=6)

        # play card directly
        game_state = step_action(base_game, Pid.P1, CardAction(
            card=GrandExpectation,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4}))
        ))
        p1 = game_state.player1
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p1ac.hp, 8)
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertIn(InspirationFieldEnhancedStatus, p1.combat_statuses)
        burst_status = p1.combat_statuses.just_find(InspirationFieldEnhancedStatus)
        self.assertEqual(burst_status.usages, 2)
        self.assertEqual(burst_status.activated, False)

        # play card with basic burst status
        game_state = AddCombatStatusEffect(
            target_pid=Pid.P1, status=InspirationFieldStatus
        ).execute(base_game)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GrandExpectation,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 4}))
        ))
        p1 = game_state.player1
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p1ac.hp, 8)
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.PYRO, p2ac.elemental_aura)
        self.assertNotIn(InspirationFieldStatus, p1.combat_statuses)
        self.assertIn(InspirationFieldEnhancedStatus, p1.combat_statuses)
        burst_status = p1.combat_statuses.just_find(InspirationFieldEnhancedStatus)
        self.assertEqual(burst_status.usages, 2)
        self.assertEqual(burst_status.activated, False)

    def test_inspiration_field_status(self):
        statuses = (InspirationFieldStatus, InspirationFieldEnhancedStatus)
        for status in statuses:
            with self.subTest(status=status):
                base_game = AddCombatStatusEffect(
                    target_pid=Pid.P1, status=status
                ).execute(self.BASE_GAME)
                base_game = kill_character(base_game, character_id=2, pid=Pid.P1, hp=4)

                # P1 normal attack
                game_state = step_skill(base_game, Pid.P1, CharacterSkill.SKILL1)
                p1ac = game_state.player1.just_get_active_character()
                p2ac = game_state.player2.just_get_active_character()
                self.assertEqual(p1ac.hp, 6)
                self.assertEqual(p2ac.hp, 8 if status is InspirationFieldStatus else 6)

                # P2 normal attack
                game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
                p1ac = game_state.player1.just_get_active_character()
                p2ac = game_state.player2.just_get_active_character()
                self.assertEqual(p1ac.hp, 5)  # because opponent AC is Rhodeia of Loch
                self.assertEqual(p2ac.hp, 8 if status is InspirationFieldStatus else 6)

                game_state = kill_character(game_state, character_id=2, pid=Pid.P1, hp=7)

                # P1 normal attack
                game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
                p1ac = game_state.player1.just_get_active_character()
                p2ac = game_state.player2.just_get_active_character()
                self.assertEqual(p1ac.hp, 7)
                self.assertEqual(p2ac.hp, 4 if status is InspirationFieldStatus else 2)

                a1, a2 = LazyAgent(), LazyAgent()
                gsm = GameStateMachine(game_state, a1, a2)

                # test that the status disappears eventually
                gsm.step_until_next_phase()
                gsm.step_until_phase(game_state.mode.action_phase)

                p1_combat_statuses = gsm.get_game_state().player1.combat_statuses
                self.assertIn(status, p1_combat_statuses)
                self.assertEqual(p1_combat_statuses.just_find(status).usages, 1)

                gsm.step_until_next_phase()
                gsm.step_until_phase(game_state.mode.action_phase)

                p1_combat_statuses = gsm.get_game_state().player1.combat_statuses
                self.assertNotIn(status, p1_combat_statuses)
