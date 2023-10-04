import unittest

from dgisim.tests.test_characters.common_imports import *


class TestMaguuKenki(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        MaguuKenki,
        char_id=2,
        card=TranscendentAutomaton,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is MaguuKenki

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate correct summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ANEMO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(ShadowswordLoneGaleSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ShadowswordLoneGaleSummon).usages, 2)

    def test_elemental_skill2(self):
        # test elemental skill generate correct summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL3,
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(ShadowswordGallopingFrostSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ShadowswordGallopingFrostSummon).usages, 2)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and triggers summon
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = UpdateSummonEffect(
            Pid.P1, ShadowswordGallopingFrostSummon(usages=1)
        ).execute(game_state)
        game_state = UpdateSummonEffect(
            Pid.P1, ShadowswordLoneGaleSummon(usages=1)
        ).execute(game_state)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ANEMO: 3}),
        )
        p1 = game_state.get_player1()
        p2cs = game_state.get_player2().get_characters()
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.get_hp(), 4)
        self.assertEqual(p2c2.get_hp(), 6)
        self.assertEqual(p2c3.get_hp(), 6)
        self.assertFalse(p2c1.get_elemental_aura().has_aura())
        self.assertFalse(p2c2.get_elemental_aura().has_aura())
        self.assertFalse(p2c3.get_elemental_aura().has_aura())
        self.assertIn(ShadowswordGallopingFrostSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ShadowswordGallopingFrostSummon).usages, 1)
        self.assertIn(ShadowswordLoneGaleSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ShadowswordLoneGaleSummon).usages, 1)

    def test_summon(self):
        # As both summons inherits the exact same parent class, and the only diff is elem.
        # Only one summon needs to be tested here.
        game_state = AddSummonEffect(
            Pid.P1, ShadowswordGallopingFrostSummon
        ).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 9)
        self.assertIn(Element.CRYO, p2ac.get_elemental_aura())
        self.assertIn(ShadowswordGallopingFrostSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(ShadowswordGallopingFrostSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.CRYO, p2ac.get_elemental_aura())
        self.assertNotIn(ShadowswordGallopingFrostSummon, p1.get_summons())

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=TranscendentAutomaton,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 3}))
        ))
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_id(), 3)

        game_state = skip_action_round(game_state, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p1ac = game_state.get_player1().just_get_active_character()
        self.assertEqual(p1ac.get_id(), 1)
