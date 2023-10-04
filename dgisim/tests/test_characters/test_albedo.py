import unittest

from dgisim.tests.test_characters.common_imports import *


class TestAlbedo(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Albedo,
        char_id=2,
        card=DescentOfDivinity,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Albedo

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill generate summon
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.GEO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 10)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())
        self.assertIn(SolarIsotomaSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(SolarIsotomaSummon).usages, 3)

    def test_elemental_burst(self):
        # burst without summon deals 4 damage
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.GEO)
        self.assertEqual(dmg.damage, 4)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # burst with summon
        game_state = AddSummonEffect(Pid.P1, SolarIsotomaSummon).execute(self.BASE_GAME)
        game_state = fill_energy_for_all(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.GEO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.GEO)
        self.assertEqual(dmg.damage, 6)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

    def test_solar_isotoma_summon(self):
        game_state = AddSummonEffect(Pid.P1, SolarIsotomaSummon).execute(self.BASE_GAME)
        game_state = grant_all_thick_shield(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)

        # test first plunge gets cost reduction
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 2})
        )

        # test second plunge doesn't get cost reduction
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )

        # test summon damage and usages behaves correctly
        game_state = remove_all_thick_shield(game_state)
        game_state = next_round_with_great_omni(game_state)
        game_state = grant_all_thick_shield(game_state)
        p1_summons = game_state.get_player1().get_summons()
        self.assertIn(SolarIsotomaSummon, p1_summons)
        self.assertEqual(p1_summons.just_find(SolarIsotomaSummon).usages, 2)
        last_summon_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(last_summon_dmg.element, Element.GEO)
        self.assertEqual(last_summon_dmg.damage, 1)
        self.assertEqual(
            last_summon_dmg.target,
            StaticTarget.from_player_active(game_state, Pid.P2),
        )

        # test cost reduction usages refreshes next round
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 2})
        )

        # test non-plunge doesn't get reduction
        game_state = next_round_with_great_omni(game_state)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        assert SolarIsotomaSummon in game_state.get_player1().get_summons()
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )

        # check summon usages decreases as expected
        p1_summons = game_state.get_player1().get_summons()
        self.assertIn(SolarIsotomaSummon, p1_summons)
        self.assertEqual(p1_summons.just_find(SolarIsotomaSummon).usages, 1)

        # check summon disappears eventually
        game_state = next_round(game_state)
        p1_summons = game_state.get_player1().get_summons()
        self.assertNotIn(SolarIsotomaSummon, p1_summons)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=DescentOfDivinity,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.GEO: 3}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = add_dmg_listener(game_state, Pid.P1)

        # test plunge gets more damage
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 2})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 3)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # test all plunges gets more damage
        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 3)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

        # test non-plunges doesn't get boost
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1, dice=ActualDice({Element.OMNI: 3})
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(dmg.damage, 2)
        self.assertEqual(dmg.target, StaticTarget.from_player_active(game_state, Pid.P2))

