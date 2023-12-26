import unittest

from src.tests.test_characters.common_imports import *


class TestTartaglia(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Tartaglia,
        char_id=2,
        card=AbyssalMayhemHydrospout,
    )

    def test_normal_attack(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        
        # test non-charged attack applis no RiptideStatus
        game_state = replace_dice(game_state, Pid.P1, ActualDice({  # odd
            Element.HYDRO: 99,
            Element.OMNI: 10,
        }))
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.HYDRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertNotIn(RiptideStatus, p2ac.get_character_statuses())

        # test charged attack applies RiptideStatus
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)

        # Test skill1 applies RiptideStatus even if dice is odd
        game_state = replace_dice(game_state, Pid.P1, ActualDice({  # odd
            Element.HYDRO: 99,
            Element.OMNI: 100,
        }))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1ac, p2ac = active_chars(game_state)
        self.assertNotIn(RangeStanceStatus, p1ac.get_character_statuses())
        self.assertIn(MeleeStanceStatus, p1ac.get_character_statuses())
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.HYDRO)

    def test_elemental_burst(self):
        base_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        base_state = fill_energy_for_all(base_state)
        assert RangeStanceStatus in p1_active_char(base_state).get_character_statuses()

        # test range burst deals correct damage, return energy and apply RiptideStatus
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1ac, p2ac = active_chars(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)
        self.assertIs(dmg.element, Element.HYDRO)
        self.assertEqual(p1ac.get_energy(), 2)
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())

        # test melee burst deals correct damage, return no energy and apply no RiptideStatus
        target = StaticTarget.from_player_active(game_state, Pid.P1)
        game_state = RemoveCharacterStatusEffect(target, RangeStanceStatus).execute(base_state)
        game_state = AddCharacterStatusEffect(target, MeleeStanceStatus).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1ac, p2ac = active_chars(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 7)
        self.assertIs(dmg.element, Element.HYDRO)
        self.assertEqual(p1ac.get_energy(), 0)
        self.assertNotIn(RiptideStatus, p2ac.get_character_statuses())

    def test_melee_stance_status(self):
        base_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        base_state = add_dmg_listener(base_state, Pid.P2)
        base_state = grant_all_infinite_revival(base_state)
        target = StaticTarget.from_player_active(base_state, Pid.P1)
        base_state = RemoveCharacterStatusEffect(target, RangeStanceStatus).execute(base_state)
        base_state = AddCharacterStatusEffect(target, MeleeStanceStatus).execute(base_state)
        base_state = replace_dice(base_state, Pid.P1, ActualDice({Element.OMNI: 100}))  # even
        assert RiptideStatus not in p2_active_char(base_state).get_character_statuses()

        # test melee stance makes physical damage hydro
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.HYDRO)
        assert RiptideStatus in p2_active_char(game_state).get_character_statuses()

        # test melee stance boosts dmg against character with RiptideStatus
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        skill_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(skill_dmg.damage, 3)
        self.assertIs(skill_dmg.element, Element.HYDRO)
        assert RiptideStatus in p2_active_char(game_state).get_character_statuses()
        piercing_dmg = get_dmg_listener_data(game_state, Pid.P1)[-2]
        self.assertEqual(piercing_dmg.damage, 1)
        self.assertIs(piercing_dmg.element, Element.PIERCING)

        # test can only pierce twice
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        skill_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(skill_dmg.damage, 3)
        self.assertIs(skill_dmg.element, Element.HYDRO)
        piercing_dmg = get_dmg_listener_data(game_state, Pid.P1)[-2]
        self.assertEqual(piercing_dmg.damage, 1)
        self.assertIs(piercing_dmg.element, Element.PIERCING)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        skill_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(skill_dmg.damage, 3)
        self.assertIs(skill_dmg.element, Element.HYDRO)
        supposed_piercing_dmg = get_dmg_listener_data(game_state, Pid.P1)[-2]
        self.assertNotEqual(supposed_piercing_dmg.damage, 1)
        self.assertIsNot(supposed_piercing_dmg.element, Element.PIERCING)

        # test can pierce again next round
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        skill_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(skill_dmg.damage, 3)
        self.assertIs(skill_dmg.element, Element.HYDRO)
        piercing_dmg = get_dmg_listener_data(game_state, Pid.P1)[-2]
        self.assertEqual(piercing_dmg.damage, 1)
        self.assertIs(piercing_dmg.element, Element.PIERCING)
        self.assertEqual(piercing_dmg.target.id, 2)

        # test "converts" back to RangeStance after 2 rounds
        game_state = next_round(game_state)
        p1ac = p1_active_char(game_state)
        self.assertNotIn(MeleeStanceStatus, p1ac.get_character_statuses())
        self.assertIn(RangeStanceStatus, p1ac.get_character_statuses())

    def test_riptide_transfer(self):
        base_state = RelativeAddCharacterStatusEffect(
            source_pid=Pid.P1,
            target=DynamicCharacterTarget.OPPO_ACTIVE,
            status=RiptideStatus,
        ).execute(self.BASE_GAME)
        base_state = kill_character(base_state, character_id=1, pid=Pid.P2, hp=1)

        # test RiptideStatus transfers on direct kill
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P2, DeathSwapAction(char_id=2))
        p2ac = p2_active_char(game_state)
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())

        # test RiptideStatus transfers on swapped kill
        game_state = replace_character(base_state, Pid.P1, Jean, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p2ac = p2_active_char(game_state)
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=AbyssalMayhemHydrospout,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 3}))
        ))
        p2ac = p2_active_char(game_state)
        self.assertIn(RiptideStatus, p2ac.get_character_statuses())
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.PIERCING)
        self.assertEqual(dmg.target.id, 1)
        assert len(get_dmg_listener_data(game_state, Pid.P1)) == 1

        # test doesn't trigger if Tartaglia is not active
        game_state = silent_fast_swap(game_state, Pid.P1, 3)  # swap to non-Tartaglia
        game_state = next_round(game_state)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 1)

        # test doesn't trigger if Opponent with Riptide is not active
        game_state = silent_fast_swap(game_state, Pid.P1, 2)  # back to Tartaglia
        game_state = silent_fast_swap(game_state, Pid.P2, 2)  # swap to non-Riptide
        game_state = next_round(game_state)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 1)
