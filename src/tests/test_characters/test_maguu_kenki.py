import unittest

from src.tests.test_characters.common_imports import *


class TestMaguuKenki(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        MaguuKenki,
        char_id=2,
        card=TranscendentAutomaton,
    )
    assert type(BASE_GAME.player1.just_get_active_character()) is MaguuKenki

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ANEMO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate correct summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ANEMO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(ShadowswordLoneGaleSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(ShadowswordLoneGaleSummon).usages, 2)

    def test_elemental_skill2(self):
        # test elemental skill generate correct summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL3,
            dice=ActualDice({Element.CRYO: 3}),
        )
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 10)
        self.assertFalse(p2ac.elemental_aura.has_aura())
        self.assertIn(ShadowswordGallopingFrostSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(ShadowswordGallopingFrostSummon).usages, 2)

    def test_elemental_burst(self):
        # test burst has correct amount of damage and triggers summon
        game_state = recharge_energy_for_all(self.BASE_GAME)
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
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        p2c1, p2c2, p2c3 = p2cs.get_characters()
        self.assertEqual(p2c1.hp, 4)
        self.assertEqual(p2c2.hp, 6)
        self.assertEqual(p2c3.hp, 6)
        self.assertFalse(p2c1.elemental_aura.has_aura())
        self.assertFalse(p2c2.elemental_aura.has_aura())
        self.assertFalse(p2c3.elemental_aura.has_aura())
        self.assertIn(ShadowswordGallopingFrostSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(ShadowswordGallopingFrostSummon).usages, 1)
        self.assertIn(ShadowswordLoneGaleSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(ShadowswordLoneGaleSummon).usages, 1)

    def test_summon(self):
        # As both summons inherits the exact same parent class, and the only diff is elem.
        # Only one summon needs to be tested here.
        game_state = AddSummonEffect(
            Pid.P1, ShadowswordGallopingFrostSummon
        ).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 9)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertIn(ShadowswordGallopingFrostSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(ShadowswordGallopingFrostSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.player1
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertIn(Element.CRYO, p2ac.elemental_aura)
        self.assertNotIn(ShadowswordGallopingFrostSummon, p1.summons)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=TranscendentAutomaton,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 3}))
        ))
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.id, 3)

        game_state = skip_action_round(game_state, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        p1ac = game_state.player1.just_get_active_character()
        self.assertEqual(p1ac.id, 1)
