import unittest

from src.tests.test_characters.common_imports import *


class TestKujouSara(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        KujouSara,
        char_id=2,
        card=SinOfPride,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.ELECTRO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ELECTRO)
        self.assertIn(TenguJuuraiAmbushSummon, game_state.player1.summons)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ELECTRO: 4}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ELECTRO)
        self.assertIn(TenguJuuraiStormclusterSummon, game_state.player1.summons)

    def test_ambush_summon(self):
        game_state = AddSummonEffect(Pid.P1, TenguJuuraiAmbushSummon).execute(self.BASE_GAME)
        game_state = replace_character(game_state, Pid.P1, Kaeya, 1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = next_round(game_state)
        self.assertNotIn(TenguJuuraiAmbushSummon, game_state.player1.summons)
        self.assertIn(CrowfeatherCoverStatus, p1_active_char(game_state).character_statuses)

    def test_stormcluster_summon(self):
        game_state = AddSummonEffect(Pid.P1, TenguJuuraiStormclusterSummon).execute(self.BASE_GAME)
        summon = game_state.player1.summons.just_find(TenguJuuraiStormclusterSummon)
        assert summon.usages == 2
        game_state = replace_character(game_state, Pid.P1, Kaeya, 1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = next_round(game_state)
        self.assertIn(TenguJuuraiStormclusterSummon, game_state.player1.summons)
        summon = game_state.player1.summons.just_find(TenguJuuraiStormclusterSummon)
        self.assertEqual(summon.usages, 1)
        self.assertIn(CrowfeatherCoverStatus, p1_active_char(game_state).character_statuses)

    def test_crowfeather_cover_status(self):
        game_state = replace_character(self.BASE_GAME, Pid.P1, Kaeya, 1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)

        # test only elemental skill and burst gets buffed
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=CrowfeatherCoverStatus,
        ).execute(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        status = p1_active_char(game_state).character_statuses.just_find(CrowfeatherCoverStatus)
        self.assertEqual(status.usages, 2)

        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        status = p1_active_char(game_state).character_statuses.just_find(CrowfeatherCoverStatus)
        self.assertEqual(status.usages, 1)

        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertNotIn(CrowfeatherCoverStatus, p1_active_char(game_state).character_statuses)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = replace_character(game_state, Pid.P1, Kaeya, 1)
        game_state = replace_character(game_state, Pid.P1, Keqing, 3)
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SinOfPride,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ELECTRO: 3})),
        ))
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = next_round_with_great_omni(game_state)
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = next_round_with_great_omni(game_state)
        p1c1, _, p1c3 = game_state.player1.characters.get_characters()
        assert CrowfeatherCoverStatus in p1c1.character_statuses
        assert CrowfeatherCoverStatus in p1c3.character_statuses
        game_state = end_round(game_state, Pid.P2)
        game_state = use_elemental_aura(game_state, None, Pid.P2)

        # test talent is not effective when character's elemental type is not ELECTRO
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)

        # test talent is effective when character is ELECTRO
        game_state = use_elemental_aura(game_state, None, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, 3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)

        # test talent not effective when Kujou is defeated
        game_state = kill_character(game_state, 2, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
