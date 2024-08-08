import random
import unittest

from src.dgisim.element import PURE_ELEMENTS
from src.tests.test_characters.common_imports import *


def p1_bogglecat_box(game_state: GameState) -> BogglecatBoxSummon:
    return game_state.player1.summons.just_find(BogglecatBoxSummon)


class TestLynette(unittest.TestCase):
    BASE_STATE = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Lynette,
        char_id=2,
        card=AColdBladeLikeAShadow,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.ANEMO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL, normal_attack=True, num=1,
        )

    def test_skill2(self):
        base_state = add_dmg_listener(self.BASE_STATE, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        assert p2_active_char(base_state).id == 1
        assert p1_active_char(base_state).hp == 10
        
        """ check first skill dmg as usual when full hp """
        for hp in (10, 9):
            with self.subTest(hp=hp):
                game_state = base_state
                game_state = set_hp(game_state, Pid.P1, hp)
                game_state = step_skill(
                    game_state, Pid.P1, CharacterSkill.SKILL2,
                    cost=ActualDice({Element.ANEMO: 3}),
                )
                assert_last_dmg(
                    self, game_state, Pid.P1, amount=3, elem=Element.ANEMO,
                    num=1, elemental_skill=True,
                )
                self.assertNotIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)

        """ check first skill dmg when hp <= 8 """
        for hp in (8, 7, 6):
            with self.subTest(hp=hp):
                game_state = base_state
                game_state = set_hp(game_state, Pid.P1, hp)
                game_state = add_healing_listener(game_state, Pid.P1)
                game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
                assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.ANEMO)
                self.assertEqual(p2_active_char(game_state).id, 1)
                self.assertIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)
                game_state = assert_last_healing(
                    self, game_state, Pid.P1, amount=2, num=1, clear=True,
                    target=StaticTarget.from_player_active(game_state, Pid.P1),
                )

        # check only effective the first skill2 per round
        game_state = set_hp(game_state, Pid.P1, 8)
        game_state = remove_character_status(game_state, Pid.P1, OverawingAssaultStatus)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.ANEMO)
        self.assertEqual(p2_active_char(game_state).id, 1)
        self.assertNotIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)
        assert_last_healing(self, game_state, Pid.P1, num=0)

        # refreshes the next round
        game_state = next_round_with_great_omni(game_state, Pid.P1)
        assert OverawingAssaultStatus not in p1_active_char(game_state).character_statuses
        game_state = set_hp(game_state, Pid.P1, 8)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p2_active_char(game_state).id, 1)
        self.assertIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)
        game_state = assert_last_healing(
            self, game_state, Pid.P1, amount=2, num=1, clear=True,
            target=StaticTarget.from_player_active(game_state, Pid.P1),
        )

        # first non-skill2 skill doesn't count
        game_state = base_state
        game_state = add_healing_listener(game_state, Pid.P1)
        game_state = set_hp(game_state, Pid.P1, 8)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = set_hp(game_state, Pid.P1, 8)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        game_state = set_hp(game_state, Pid.P1, 8)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=3, elem=Element.ANEMO)
        self.assertEqual(p2_active_char(game_state).id, 1)
        self.assertIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)
        game_state = assert_last_healing(
            self, game_state, Pid.P1, amount=2, num=1, clear=True,
            target=StaticTarget.from_player_active(game_state, Pid.P1),
        )

    def test_elemental_burst(self):
        game_state = self.BASE_STATE
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.ANEMO: 3}),
        )
        assert_last_dmg(
            self, game_state, Pid.P1, amount=2, elem=Element.ANEMO,
            num=1, elemental_burst=True,
        )
        self.assertIn(BogglecatBoxSummon, game_state.player1.summons)
        self.assertEqual(p1_bogglecat_box(game_state).usages, 2)
        self.assertIs(p1_bogglecat_box(game_state).elem, Element.ANEMO)

    def test_overawing_assault_status(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_character_status(base_state, Pid.P1, OverawingAssaultStatus)

        """ check only -2 hp if hp >= 6 """
        for hp in (4, 5, 6, 7, 8):
            with self.subTest(hp=hp):
                game_state = base_state
                game_state = set_hp(game_state, Pid.P1, hp)
                game_state = next_round(game_state, Pid.P1)
                self.assertNotIn(OverawingAssaultStatus, p1_active_char(game_state).character_statuses)
                if hp < 6:
                    assert_last_dmg(self, game_state, Pid.P1, num=0)
                else:
                    assert_last_dmg(
                        self, game_state, Pid.P1, amount=2, elem=Element.PIERCING, status=True,
                        target=StaticTarget.from_player_active(game_state, Pid.P1), num=1,
                    )

    def test_bogglecat_box(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = add_summon(base_state, Pid.P1, BogglecatBoxSummon)
        base_state = grant_all_infinite_revival(base_state)
        assert p1_bogglecat_box(base_state).usages == 2
        assert p1_bogglecat_box(base_state).elem == Element.ANEMO
        assert p1_bogglecat_box(base_state).available

        """ check elem conversion when taking convertable dmg for the first time """
        for elem in PURE_ELEMENTS:
            char_id = random.choice((1, 2, 3))
            dmg = random.randint(0, 3)
            with self.subTest(elem=elem, char_id=char_id, dmg=dmg):
                game_state = base_state
                game_state = simulate_status_dmg(game_state, dmg, elem, Pid.P1, char_id=char_id) #, observe=elem in Reaction.SWIRL.first_elems)

                self.assertEqual(p1_bogglecat_box(game_state).usages, 2)
                if dmg > 0 and char_id == game_state.player1.just_get_active_character().id:
                    assert_last_dmg(self, game_state, Pid.P1, amount=dmg - 1)
                    self.assertFalse(p1_bogglecat_box(game_state).available)
                else:
                    assert_last_dmg(self, game_state, Pid.P1, amount=dmg)
                    self.assertTrue(p1_bogglecat_box(game_state).available)

                if elem in Reaction.SWIRL.first_elems:
                    self.assertIs(p1_bogglecat_box(game_state).elem, elem)
                    new_elem = random.choice(tuple(Reaction.SWIRL.first_elems - {elem}))
                    game_state = simulate_status_dmg(game_state, 1, new_elem, Pid.P1, char_id=char_id)
                    self.assertIs(p1_bogglecat_box(game_state).elem, elem)
                else:
                    self.assertIs(p1_bogglecat_box(game_state).elem, Element.ANEMO)

                elem = elem if elem in Reaction.SWIRL.first_elems else Element.ANEMO
                game_state = remove_aura(game_state, Pid.P2)
                game_state = next_round(game_state, Pid.P1)
                self.assertTrue(p1_bogglecat_box(game_state).available)
                assert_last_dmg(
                    self, game_state, Pid.P1, amount=1, elem=elem, summon=True,
                    target=StaticTarget.from_player_active(game_state, Pid.P2)
                )
                self.assertEqual(p1_bogglecat_box(game_state).usages, 1)

    def test_talent_card(self):
        base_state = self.BASE_STATE
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        assert p2_active_char(base_state).id == 1

        """ check 2nd skill2 dmg + 2 and backward swap opponent """
        game_state = base_state
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ANEMO, num=1, clear=True,
        )
        self.assertEqual(p2_active_char(game_state).id, 1)

        game_state = play_dice_only_card(
            game_state, Pid.P1, AColdBladeLikeAShadow, cost=ActualDice({Element.ANEMO: 3}),
        )
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=5, elem=Element.ANEMO, num=1, clear=True,
            target=StaticTarget.from_char_id(Pid.P2, 1),
        )
        self.assertEqual(p2_active_char(game_state).id, 3)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ANEMO, num=1, clear=True,
        )
        self.assertEqual(p2_active_char(game_state).id, 3)

        # check refreshes the next round (and only skill2 count)
        game_state = next_round_with_great_omni(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        game_state = assert_last_dmg(self, game_state, Pid.P1, clear=True)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ANEMO, num=1, clear=True,
        )
        self.assertEqual(p2_active_char(game_state).id, 3)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=5, elem=Element.ANEMO, num=1, clear=True,
            target=StaticTarget.from_char_id(Pid.P2, 3),
        )
        self.assertEqual(p2_active_char(game_state).id, 2)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=3, elem=Element.ANEMO, num=1, clear=True,
        )
        self.assertEqual(p2_active_char(game_state).id, 2)
