import unittest

from src.tests.test_characters.common_imports import *


def p1_the_wolf_within(game_state: GameState) -> TheWolfWithinStatus:
    return game_state.player1.characters.just_get_character(2).character_statuses.just_find(TheWolfWithinStatus)


class TestRazor(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Razor,
        char_id=2,
        card=Awakening,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.ELECTRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL, normal_attack=True, num=1,
        )

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ELECTRO, elemental_skill=True, num=1,
        )

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ELECTRO, num=1, elemental_burst=True,
        )
        self.assertIn(TheWolfWithinStatus, p1_active_char(game_state).character_statuses)
        self.assertEqual(p1_the_wolf_within(game_state).usages, 2)

    def test_the_wolf_within_status(self):
        base_state = self.BASE_STATE
        base_state = add_character_status(base_state, Pid.P1, TheWolfWithinStatus)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        assert p1_the_wolf_within(base_state).usages, 2

        """ check additional damage when skill1 or 2 is used """
        game_state = base_state
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.ELECTRO, status=True, num=2, clear=True,
        )
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.ELECTRO, status=True, num=2, clear=True,
        )
        self.assertEqual(p1_the_wolf_within(game_state).usages, 2)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        game_state = assert_last_dmg(self, game_state, Pid.P1, elemental_burst=True, num=1, clear=True)
        self.assertEqual(p1_the_wolf_within(game_state).usages, 2)

        # check usages - 1 per round end
        game_state = next_round(game_state)
        self.assertEqual(p1_the_wolf_within(game_state).usages, 1)
        game_state = next_round(game_state)
        self.assertNotIn(TheWolfWithinStatus, p1_active_char(game_state).character_statuses)

    def test_talent_card(self):
        base_state = self.BASE_STATE
        base_state = replace_characters(base_state, Pid.P1, (Kaeya, None, Keqing))
        base_state = grant_all_infinite_revival(base_state)
        assert Kaeya.from_default().max_energy == 2
        assert Keqing.from_default().max_energy == 3
        assert p1_active_char(base_state).energy == 0

        """ check talent when self energy is not full """
        game_state = base_state
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        self.assertEqual(p1_active_char(game_state).energy, 2)

        # once per round
        game_state = drain_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 1)

        # resets the next round (and skill1 doesn't count)
        game_state = next_round_with_great_omni(game_state, Pid.P1) 
        game_state = drain_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(p1_active_char(game_state).energy, 1)

        game_state = drain_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 2)

        """ check energy recharge priority """
        game_state = base_state
        game_state = recharge_energies_for(game_state, Pid.P1, (1, 1, 1))
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_energies(self, game_state, Pid.P1, (1, 2, 2))

        game_state = base_state
        game_state = recharge_energies_for(game_state, Pid.P1, (1, 2, 1))
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_energies(self, game_state, Pid.P1, (1, 2, 2))

        game_state = base_state
        game_state = recharge_energies_for(game_state, Pid.P1, (1, 1, 2))
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_energies(self, game_state, Pid.P1, (1, 2, 3))

        game_state = base_state
        game_state = recharge_energies_for(game_state, Pid.P1, (1, 1, 3))
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_energies(self, game_state, Pid.P1, (2, 2, 3))

        # check usages - 1 even if all energies are full
        game_state = base_state
        game_state = recharge_energies_for(game_state, Pid.P1, (2, 2, 3))
        game_state = play_dice_only_card(
            game_state, Pid.P1, Awakening, cost=ActualDice({Element.ELECTRO: 3}),
        )
        assert_energies(self, game_state, Pid.P1, (2, 2, 3))

        game_state = drain_energies_for(game_state, Pid.P1, (0, 0, 0))
        assert_energies(self, game_state, Pid.P1, (0, 0, 0))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_energies(self, game_state, Pid.P1, (0, 1, 0))
