import unittest

from src.tests.test_characters.common_imports import *


def p1_takimeguri_kanka(game_state: GameState) -> TakimeguriKankaStatus:
    return game_state.player1.characters.just_get_character(2).character_statuses.just_find(TakimeguriKankaStatus)


def p1_garden_of_purity(game_state: GameState) -> GardenOfPuritySummon:
    return game_state.player1.summons.just_find(GardenOfPuritySummon)


class TestKamisatoAyato(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        KamisatoAyato,
        char_id=2,
        card=KyoukaFuushi,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.HYDRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL, normal_attack=True,
        )

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.HYDRO,
            num=1, elemental_skill=True,
        )
        self.assertIn(TakimeguriKankaStatus, p1_active_char(game_state).character_statuses)
        self.assertEqual(p1_takimeguri_kanka(game_state).usages, 3)

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=3)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.HYDRO,
            num=1, elemental_burst=True,
        )
        self.assertIn(GardenOfPuritySummon, game_state.player1.summons)
        self.assertEqual(p1_garden_of_purity(game_state).usages, 2)

    def test_takimeguri_kanka_status(self):
        game_state = self.BASE_STATE
        game_state = add_character_status(game_state, Pid.P1, TakimeguriKankaStatus)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = replace_character(game_state, Pid.P1, Bennett, 1)
        self.assertEqual(p1_takimeguri_kanka(game_state).usages, 3)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.HYDRO, normal_attack=True, num=1, clear=True,
        )
        self.assertEqual(p1_takimeguri_kanka(game_state).usages, 2)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.HYDRO, normal_attack=True, num=1, clear=True,
        )
        self.assertEqual(p1_takimeguri_kanka(game_state).usages, 1)

        # check teammate doesn't trigger
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL, clear=True)
        self.assertEqual(p1_takimeguri_kanka(game_state).usages, 1)

        game_state = step_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.HYDRO, normal_attack=True, num=1, clear=True,
        )
        self.assertNotIn(TakimeguriKankaStatus, p1_active_char(game_state).character_statuses)

    def test_garden_of_purity(self):
        game_state = self.BASE_STATE
        game_state = replace_characters(game_state, Pid.P1, (Kaeya, None, Klee))
        game_state = replace_characters(game_state, Pid.P2, (Kaeya, Kaeya, Kaeya))
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = add_dmg_listener(game_state, Pid.P2)
        game_state = add_aura_remover(game_state, Pid.P2)
        game_state = add_summon(game_state, Pid.P1, GardenOfPuritySummon)
        game_state = grant_all_infinite_revival(game_state)
        self.assertEqual(p1_garden_of_purity(game_state).usages, 2)

        """ check not boost opponent normal attacks """
        game_state = reactivate_player(game_state, Pid.P2)
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P2, amount=2)

        """ check boost team normal attacks """
        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = step_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.PHYSICAL)
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO)

        """ check summon dmg """
        game_state = next_round(game_state)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.HYDRO)
        self.assertEqual(p1_garden_of_purity(game_state).usages, 1)

        game_state = next_round(game_state)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.HYDRO)
        self.assertNotIn(GardenOfPuritySummon, game_state.player1.summons)

    def test_talent_card(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = play_dice_only_card(base_state, Pid.P1, KyoukaFuushi, cost=ActualDice({Element.HYDRO: 3}))

        assert TakimeguriKankaStatus in p1_active_char(base_state).character_statuses

        """ check +2 dmg only when opponent hp < 6 """
        game_state = base_state
        game_state = set_hp(game_state, Pid.P2, hp=7)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=3)

        game_state = base_state
        game_state = set_hp(game_state, Pid.P2, hp=6)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=5)

        game_state = set_hp(game_state, Pid.P2, hp=5)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=5)

        """ check only effective when triggers Takimeguri Kanka """
        game_state = base_state
        game_state = remove_character_status(game_state, Pid.P1, TakimeguriKankaStatus)
        game_state = set_hp(game_state, Pid.P2, hp=6)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
