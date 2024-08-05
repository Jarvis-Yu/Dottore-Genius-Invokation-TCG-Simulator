import unittest

from src.tests.test_characters.common_imports import *


def p1_melody_loop(game_state: GameState) -> MelodyLoopSummon:
    return game_state.player1.summons.just_find(MelodyLoopSummon)


class TestBarbara(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Barbara,
        char_id=2,
        card=GloriousSeason,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.HYDRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=1, elem=Element.HYDRO, normal_attack=True)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.HYDRO,
            num=1, elemental_skill=True,
        )
        self.assertIn(MelodyLoopSummon, game_state.player1.summons)
        self.assertEqual(p1_melody_loop(game_state).usages, 2)

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = add_healing_listener(game_state, Pid.P1)
        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=1)
        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=2)
        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=3)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=3)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.HYDRO: 3}),
        )
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 0)
        assert_last_healing(
            self, game_state, Pid.P1, last_index=2, amount=4,
            target=StaticTarget.from_char_id(Pid.P1, 2),
        )
        assert_last_healing(
            self, game_state, Pid.P1, last_index=1, amount=4,
            target=StaticTarget.from_char_id(Pid.P1, 3),
        )
        assert_last_healing(
            self, game_state, Pid.P1, last_index=0, amount=4, num=3,
            target=StaticTarget.from_char_id(Pid.P1, 1),
        )

    def test_melody_loop_summon(self):
        game_state = self.BASE_STATE
        game_state = add_healing_listener(game_state, Pid.P1)
        game_state = add_summon(game_state, Pid.P1, MelodyLoopSummon)
        self.assertEqual(p1_melody_loop(game_state).usages, 2)

        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=1)
        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=2)
        game_state = set_hp(game_state, Pid.P1, hp=1, char_id=3)

        """ check healings, element application """
        game_state = next_round(game_state)
        p1c1, p1c2, p1c3 = p1_chars(game_state)
        self.assertNotIn(Element.HYDRO, p1c1.elemental_aura)
        self.assertIn(Element.HYDRO, p1c2.elemental_aura)
        self.assertNotIn(Element.HYDRO, p1c3.elemental_aura)
        assert_last_healing(
            self, game_state, Pid.P1, last_index=2, amount=1,
            target=StaticTarget.from_char_id(Pid.P1, 2),
        )
        assert_last_healing(
            self, game_state, Pid.P1, last_index=1, amount=1,
            target=StaticTarget.from_char_id(Pid.P1, 3),
        )
        assert_last_healing(
            self, game_state, Pid.P1, last_index=0, amount=1, num=3,
            target=StaticTarget.from_char_id(Pid.P1, 1),
        )
        self.assertEqual(p1_melody_loop(game_state).usages, 1)

        # disappears next round
        game_state = next_round(game_state)
        self.assertNotIn(MelodyLoopSummon, game_state.player1.summons)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = play_dice_only_card(
            game_state, Pid.P1, GloriousSeason, cost=ActualDice({Element.HYDRO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.HYDRO,
            num=1, elemental_skill=True,
        )
        self.assertIn(MelodyLoopSummon, game_state.player1.summons)
        self.assertEqual(p1_melody_loop(game_state).usages, 2)
        self.assertIn(GloriousSeasonStatus, p1_active_char(game_state).character_statuses)

        """ check swap cost reduction (before combat status), once per round """
        game_state = add_combat_status(game_state, Pid.P1, ChangingShiftsStatus)
        game_state = step_swap(game_state, Pid.P1, 1, cost=0)
        self.assertIn(ChangingShiftsStatus, game_state.player1.combat_statuses)
        game_state = remove_combat_status(game_state, Pid.P1, ChangingShiftsStatus)

        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
        game_state = step_swap(game_state, Pid.P1, 3, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)

        # check resets per round
        game_state = next_round_with_great_omni(game_state)
        assert MelodyLoopSummon in game_state.player1.summons
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 1, cost=0)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)

        """ check not usable when Melody Loop is not present """
        game_state = next_round_with_great_omni(game_state)
        assert MelodyLoopSummon not in game_state.player1.summons
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 1, cost=1)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
