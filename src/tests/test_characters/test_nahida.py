import unittest

from src.tests.test_characters.common_imports import *


class TestNahida(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Nahida.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(TheSeedOfStoredKnowledge)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Nahida

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
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.DENDRO, p2ac.elemental_aura)

    def test_elemental_skill1(self):
        # without reaction and prior Seed of Skandha Status
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
        p2cs = gsm.get_game_state().player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 2)

        # with reaction and no prior Seed of Skandha Status
        game_state = oppo_aura_elem(self.BASE_GAME, Element.ELECTRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertNotIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 1)

        # with no reaction but prior Seed of Skandha Status
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
            status=SeedOfSkandhaStatus(usages=1),
        ).execute(self.BASE_GAME)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 8)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 2)
        p2c2_status = p2c2.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c2_status.usages, 2)
        p2c3_status = p2c3.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c3_status.usages, 2)

        # with reaction and prior Seed of Skandha Status
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
            status=SeedOfSkandhaStatus(usages=1),
        ).execute(self.BASE_GAME)
        game_state = oppo_aura_elem(game_state, Element.PYRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertNotIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 1)
        p2c2_status = p2c2.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c2_status.usages, 1)
        p2c3_status = p2c3.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c3_status.usages, 1)

    def test_elemental_skill2(self):
        # without reaction
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL3,
            ActualDice({Element.OMNI: 5}),
        )

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 7)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 2)
        p2c2_status = p2c2.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c2_status.usages, 2)
        p2c3_status = p2c3.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c3_status.usages, 2)

        # with reaction
        game_state = oppo_aura_elem(self.BASE_GAME, Element.HYDRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 5)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 9)
        self.assertNotIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 1)
        p2c2_status = p2c2.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c2_status.usages, 1)
        p2c3_status = p2c3.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c3_status.usages, 1)

    def test_elemental_burst(self):
        game_state = recharge_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            ActualDice({Element.OMNI: 3}),
        )

        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 6)
        self.assertIn(Element.DENDRO, p2ac.elemental_aura)
        self.assertIn(ShrineOfMayaStatus, p1.combat_statuses)
        burst_status = p1.combat_statuses.just_find(ShrineOfMayaStatus)
        self.assertEqual(burst_status.usages, 2)

    def test_talent_card(self):
        base_state = recharge_energy_for_all(self.BASE_GAME)
        base_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
            status=SeedOfSkandhaStatus(usages=2),
        ).execute(base_state)
        base_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 2),
            status=SeedOfSkandhaStatus(usages=1),
        ).execute(base_state)

        # test with Electro and Hydro
        self.assertTrue(any(
            char.ELEMENT is Element.ELECTRO for char in base_state.player1.characters
        ))
        self.assertTrue(any(
            char.ELEMENT is Element.HYDRO for char in base_state.player1.characters
        ))
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=TheSeedOfStoredKnowledge,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 6)
        self.assertEqual(p2c2.hp, 10)
        self.assertEqual(p2c3.hp, 10)
        self.assertIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 3)
        p2c2_status = p2c2.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c2_status.usages, 2)
        self.assertIn(ShrineOfMayaStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(ShrineOfMayaStatus).usages, 3)

        # test with Pyro
        base_state = base_state.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().character(
                    Klee.from_default(1)
                ).character(
                    AratakiItto.from_default(3)
                ).build()
            ).build()
        ).build()
        base_state = oppo_aura_elem(base_state, Element.HYDRO)
        self.assertTrue(any(
            char.ELEMENT is Element.PYRO for char in base_state.player1.characters
        ))
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=TheSeedOfStoredKnowledge,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertEqual(p2c1.hp, 4)
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 10)
        self.assertIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c3.character_statuses)
        p2c1_status = p2c1.character_statuses.just_find(SeedOfSkandhaStatus)
        self.assertEqual(p2c1_status.usages, 1)
        self.assertIn(ShrineOfMayaStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(ShrineOfMayaStatus).usages, 2)

    def test_seed_of_skandha_status(self):
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 1),
            status=SeedOfSkandhaStatus(usages=2),
        ).execute(self.BASE_GAME)
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget(Pid.P2, Zone.CHARACTERS, 2),
            status=SeedOfSkandhaStatus(usages=1),
        ).execute(game_state)
        game_state = kill_character(game_state, char_id=1, hp=3)
        game_state = oppo_aura_elem(game_state, Element.ELECTRO)
        base_state = game_state

        """
        normal attack triggers seeds which kill opponent active character,
        but opponent cannot get to choose active character until all seeds are
        triggered
        """
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)

        p2cs = game_state.player2.characters
        p2c1 = p2cs.just_get_character(1)
        p2c2 = p2cs.just_get_character(2)
        p2c3 = p2cs.just_get_character(3)
        self.assertTrue(p2c1.is_defeated())
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 10)
        self.assertNotIn(Element.DENDRO, p2c1.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c2.elemental_aura)
        self.assertNotIn(Element.DENDRO, p2c3.elemental_aura)
        self.assertNotIn(SeedOfSkandhaStatus, p2c1.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c2.character_statuses)
        self.assertNotIn(SeedOfSkandhaStatus, p2c3.character_statuses)

        """
        skill triggers reaction that kills opponent active character,
        seeds get triggered normally (before death swap)
        """
        game_state = replace_character(base_state, Pid.P1, Noelle, char_id=3)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=3)
        game_state = AddCharacterStatusEffect(
            StaticTarget.from_player_active(game_state, Pid.P1),
            status=WolfsGravestoneStatus,
        ).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p2c1, p2c2, p2c3 = game_state.player2.characters.get_characters()
        self.assertTrue(p2c1.is_defeated())
        self.assertEqual(p2c2.hp, 9)
        self.assertEqual(p2c3.hp, 10)

    def test_shine_of_maya_status(self):
        game_state = AddCombatStatusEffect(
            target_pid=Pid.P1,
            status=ShrineOfMayaStatus,
        ).execute(self.BASE_GAME)
        game_state = oppo_aura_elem(game_state, Element.PYRO)

        # test character reaction dmg boosted
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)

        # test usages disappear as round ends
        gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
        gsm.step_until_next_phase()
        gsm.step_until_phase(game_state.mode.action_phase)
        self.assertIn(ShrineOfMayaStatus, gsm.get_game_state().player1.combat_statuses)
        shine_of_maya_status = gsm.get_game_state().player1.combat_statuses.just_find(
            ShrineOfMayaStatus
        )
        self.assertEqual(shine_of_maya_status.usages, 1)
        gsm.step_until_next_phase()
        gsm.step_until_phase(game_state.mode.action_phase)
        self.assertNotIn(ShrineOfMayaStatus,
                         gsm.get_game_state().player1.combat_statuses)
