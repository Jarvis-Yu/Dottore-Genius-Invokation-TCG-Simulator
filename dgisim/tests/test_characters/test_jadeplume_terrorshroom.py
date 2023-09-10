import unittest

from dgisim.tests.test_characters.common_imports import *


class TestJadeplumeTerrorshroom(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        JadeplumeTerrorshroom,
        char_id=2,
        card=ProliferatingSpores,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is JadeplumeTerrorshroom

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dices=ActualDices({Element.DENDRO: 1, Element.HYDRO: 1, Element.GEO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill deals 3 dendro damage
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dices=ActualDices({Element.DENDRO: 3}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dices=ActualDices({Element.DENDRO: 3}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())

    def test_radical_vitality_status_usages(self):
        # test character start with the shield
        game_state = self.BASE_GAME
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 0)

        # dealing elemental damage increases stacks
        game_state = grant_all_thick_shield(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 1)

        # normal attack (physical) doesn't increase stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 1)

        # dealing elemental damage increases stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 2)

        # dealing elemental damage increases stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 3)

        # dealing elemental damage increases stacks (cap at 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 3)

        # burst clears all usages
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 0)

    def test_radical_vitality_status_dmg_boost(self):
        for usages in range(0, 4):
            with self.subTest(usages=usages):
                game_state = OverrideCharacterStatusEffect(
                    target=StaticTarget.from_char_id(Pid.P1, char_id=2),
                    status=RadicalVitalityStatus(usages=usages),
                ).execute(self.BASE_GAME)
                game_state = fill_energy_for_all(game_state)
                game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
                p1ac = game_state.get_player1().just_get_active_character()
                p2ac = game_state.get_player2().just_get_active_character()
                self.assertEqual(p2ac.get_hp(), 10 - (4 + usages))
                self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
                self.assertEqual(
                    p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages,
                    0
                )

    def test_radical_vitality_status_end_round(self):
        for usages in range(0, 4):
            with self.subTest(usages=usages):
                game_state = OverrideCharacterStatusEffect(
                    target=StaticTarget.from_char_id(Pid.P1, char_id=2),
                    status=RadicalVitalityStatus(usages=usages),
                ).execute(self.BASE_GAME)
                game_state = fill_energy_for_all(game_state)
                game_state = next_round(game_state)
                p1ac = game_state.get_player1().just_get_active_character()
                expected_energy = 0 if usages == 3 else 2
                expected_stacks = 0 if usages == 3 else usages
                self.assertEqual(p1ac.get_energy(), expected_energy)
                self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
                self.assertEqual(
                    p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages,
                    expected_stacks
                )

    def test_talent_card(self):
        game_state = grant_all_thick_shield(self.BASE_GAME)
        game_state = OverrideCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, char_id=2),
            status=RadicalVitalityStatus(usages=1),
        ).execute(game_state)

        # test that talent card doesn't clear existing stacks
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ProliferatingSpores,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.DENDRO: 3}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 2)

        # normal attack (physical) doesn't increase stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 2)

        # dealing elemental damage increases stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 3)
        game_state_3_stack = game_state

        # dealing elemental damage increases stacks
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 4)
        game_state_4_stack = game_state

        # 3 stacks at end phase doesn't clear energy
        game_state = next_round(game_state_3_stack)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_energy(), 2)
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 3)

        # 4 stacks at end phase clears energy
        game_state = next_round(game_state_4_stack)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_energy(), 0)
        self.assertIn(RadicalVitalityStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(RadicalVitalityStatus).usages, 0)
