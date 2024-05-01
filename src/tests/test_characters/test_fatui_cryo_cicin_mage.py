import unittest

from src.tests.test_characters.common_imports import *


class TestFatuiCryoCicinMage(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        FatuiCryoCicinMage,
        char_id=2,
        card=CicinsColdGlare,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.CRYO: 1, Element.HYDRO: 1, Element.DENDRO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.CRYO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)
        self.assertIn(CryoCicinsSummon, game_state.player1.summons)
        cryo_cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cryo_cicins.usages, 2)

    def test_burst(self):
        base_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        base_state = recharge_energy_for_all(base_state)
        for cicin_usages in range(5):
            with self.subTest(cicin_usages=cicin_usages):
                game_state = base_state
                if cicin_usages > 0:
                    game_state = UpdateSummonEffect(
                        Pid.P1, CryoCicinsSummon(usages=cicin_usages)
                    ).execute(game_state)
                game_state = step_skill(
                    game_state,
                    Pid.P1,
                    CharacterSkill.ELEMENTAL_BURST,
                    dice=ActualDice({Element.CRYO: 3}),
                )
                dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
                self.assertEqual(dmg.damage, 5)
                self.assertIs(dmg.element, Element.CRYO)
                p1ac = p1_active_char(game_state)
                self.assertIn(FlowingCicinShieldStatus, p1ac.character_statuses)
                shield_status = p1ac.character_statuses.just_find(FlowingCicinShieldStatus)
                cicin_addition = min(cicin_usages, 3)
                self.assertEqual(shield_status.usages, 1 + cicin_addition)

    def test_cryo_cicins_summon(self):
        game_state = AddSummonEffect(Pid.P1, CryoCicinsSummon).execute(self.BASE_GAME)
        assert game_state.player1.summons.just_find(CryoCicinsSummon).usages == 2
        game_state = grant_all_infinite_revival(game_state)

        # check normal attack by non-cicin-mage cannot increase usages
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 2)

        # check normal attack by opponent cicin-mage cannot increase usages
        game_state = replace_character(game_state, Pid.P2, FatuiCryoCicinMage, char_id=1)
        assert isinstance(p2_active_char(game_state), FatuiCryoCicinMage)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 2)

        # check normal attack by self's cicin-mage can increase usages
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 3)

        # check teammate taking reaction damage cannot decrease usages
        game_state = remove_aura(game_state, Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, Element.PYRO, Pid.P1, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, Element.ANEMO, Pid.P1, char_id=1)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 3)

        # check opponent cicin-mage taking reaction damage cannot decrease usages
        game_state = remove_aura(game_state, Pid.P2, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, Element.PYRO, Pid.P2, char_id=1)
        game_state = simulate_status_dmg(game_state, 1, Element.ANEMO, Pid.P2, char_id=1)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 3)

        # check self's cicin-mage taking reaction damage can decrease usages
        game_state = remove_aura(game_state, Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 1, Element.PYRO, Pid.P1, char_id=2)
        game_state = simulate_status_dmg(game_state, 1, Element.ANEMO, Pid.P1, char_id=2)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 2)

        # check cicin deals correct dmg and element at end phase
        game_state = remove_aura(game_state, Pid.P2)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.CRYO)
        cicins = game_state.player1.summons.just_find(CryoCicinsSummon)
        self.assertEqual(cicins.usages, 1)

    def test_flow_cicin_shield_status(self):
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_player_active(self.BASE_GAME, Pid.P1),
            status=FlowingCicinShieldStatus,
        ).execute(self.BASE_GAME)
        assert p1_active_char(game_state).character_statuses.just_find(FlowingCicinShieldStatus).usages == 1
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, Pid.P1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertNotIn(FlowingCicinShieldStatus, game_state.player1.combat_statuses)

    def test_talent_card(self):
        game_state = end_round(self.BASE_GAME, Pid.P2)
        game_state = grant_all_infinite_revival(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CicinsColdGlare,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 3})),
        ))
        
        # check usages-exceeding action causes additional dmg by cicins
        ## non-exceeding action cuase no additional dmg ##
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 1)
        assert game_state.player1.summons.just_find(CryoCicinsSummon).usages == 3
        ## exceeding action causes additional dmg ##
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        _, cicin_dmg = dmgs
        self.assertEqual(cicin_dmg.damage, 2)
        self.assertIs(cicin_dmg.element, Element.CRYO)
        assert game_state.player1.summons.just_find(CryoCicinsSummon).usages == 3
        ## check usages exceeding by skill 2 ##
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        _, cicin_dmg = dmgs
        self.assertEqual(cicin_dmg.damage, 2)
        self.assertIs(cicin_dmg.element, Element.CRYO)
        assert game_state.player1.summons.just_find(CryoCicinsSummon).usages == 3
        ## check exceeding when usages was 2 ##
        game_state = OverrideSummonEffect(Pid.P1, CryoCicinsSummon(usages=2)).execute(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        _, cicin_dmg = dmgs
        self.assertEqual(cicin_dmg.damage, 2)
        self.assertIs(cicin_dmg.element, Element.CRYO)
        assert game_state.player1.summons.just_find(CryoCicinsSummon).usages == 3
        ## check non-exceeding when using skill 2 ##
        game_state = OverrideSummonEffect(Pid.P1, CryoCicinsSummon(usages=1)).execute(game_state)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 1)
