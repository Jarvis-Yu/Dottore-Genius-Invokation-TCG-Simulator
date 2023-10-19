import unittest

from src.tests.test_characters.common_imports import *


class TestSangonomiyaKokomi(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        SangonomiyaKokomi,
        char_id=2,
        card=TamakushiCasket,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is SangonomiyaKokomi

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.HYDRO: 1, Element.ELECTRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate summon and applies hydro aura
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.HYDRO: 3}),
        )
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(Element.HYDRO, p1ac.get_elemental_aura())
        self.assertIn(BakeKurageSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BakeKurageSummon).usages, 2)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and generates status
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.HYDRO: 3}),
        )
        p1ac = game_state.get_player1().just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 2)

    def test_bake_kurage_summon(self):
        # test summon heals active and damages oppo
        game_state = AddSummonEffect(Pid.P1, BakeKurageSummon).execute(self.BASE_GAME)
        game_state = simulate_status_dmg(game_state, dmg_amount=2, pid=Pid.P1)
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_hp(), 9)
        self.assertIn(BakeKurageSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BakeKurageSummon).usages, 1)

        # disappears next round
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_hp(), 10)
        self.assertNotIn(BakeKurageSummon, p1.get_summons())

    def test_ceremonial_garment_status(self):
        # normal attack has boost damage and heals
        game_state = AddCharacterStatusEffect(
            StaticTarget.from_char_id(Pid.P1, 2),
            status=CeremonialGarmentStatus,
        ).execute(self.BASE_GAME)
        game_state = simulate_status_dmg(game_state, dmg_amount=6, pid=Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, dmg_amount=5, pid=Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, dmg_amount=4, pid=Pid.P1, char_id=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.get_player1().just_get_active_character()
        p1cs = game_state.get_player1().get_characters()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 2)
        self.assertEqual(p1cs.just_get_character(1).get_hp(), 5)
        self.assertEqual(p1cs.just_get_character(2).get_hp(), 6)
        self.assertEqual(p1cs.just_get_character(3).get_hp(), 7)

        # ally cannot trigger
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1cs = game_state.get_player1().get_characters()
        self.assertEqual(p1cs.just_get_character(1).get_hp(), 5)
        self.assertEqual(p1cs.just_get_character(2).get_hp(), 6)
        self.assertEqual(p1cs.just_get_character(3).get_hp(), 7)

        # usages decrease per round
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = next_round(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 1)

        # usages decrease per round
        game_state = next_round(game_state)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertNotIn(CeremonialGarmentStatus, p1ac.get_character_statuses())

    def test_talent_card(self):
        # test talent burst refreshes summon usages
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = OverrideSummonEffect(Pid.P1, BakeKurageSummon(usages=1)).execute(game_state)
        game_state = simulate_status_dmg(game_state, dmg_amount=5, pid=Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TamakushiCasket,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 3}))
        ), observe=False)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_hp(), 6)
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 2)
        self.assertIn(BakeKurageSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BakeKurageSummon).usages, 2)

        # test talent boosts summon damage
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_hp(), 7)
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 1)
        self.assertIn(BakeKurageSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BakeKurageSummon).usages, 1)

        # burst normal attack functions as usual
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = fill_dice_with_omni(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1 = game_state.get_player1()
        p1ac = p1.just_get_active_character()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertIn(Element.HYDRO, p2ac.get_elemental_aura())
        self.assertEqual(p1ac.get_hp(), 8)
        self.assertIn(CeremonialGarmentStatus, p1ac.get_character_statuses())
        self.assertEqual(p1ac.get_character_statuses().just_find(CeremonialGarmentStatus).usages, 1)
        self.assertIn(BakeKurageSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(BakeKurageSummon).usages, 1)
