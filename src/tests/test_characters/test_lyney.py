import unittest

from src.tests.test_characters.common_imports import *


class TestLyney(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Lyney,
        char_id=2,
        card=ConclusiveOvation,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.PYRO: 1, Element.HYDRO: 1, Element.CRYO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = end_round(game_state, Pid.P2)

        # check self-damage when hp >= 6
        game_state = kill_character(game_state, char_id=2, pid=Pid.P1, hp=6)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        dmg, self_dmg = dmgs
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertEqual(self_dmg.damage, 1)
        self.assertIs(self_dmg.element, Element.PIERCING)
        self.assertIn(GrinMalkinHatSummon, game_state.player1.summons)
        hat_summon = game_state.player1.summons.just_find(GrinMalkinHatSummon)
        self.assertEqual(hat_summon.usages, 1)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 1)

        # check no self-damage when hp < 6
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.PYRO: 3}),
        )
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 1)
        dmg = dmgs[0]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertIn(GrinMalkinHatSummon, game_state.player1.summons)
        hat_summon = game_state.player1.summons.just_find(GrinMalkinHatSummon)
        self.assertEqual(hat_summon.usages, 2)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 2)

    def test_skill3(self):
        # check basic skill deals 3 pyro damage and that's it
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = simulate_status_dmg(game_state, 7, pid=Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertEqual(p1_active_char(game_state).hp_lost(), 7)

    def test_elemental_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertIn(GrinMalkinHatSummon, game_state.player1.summons)
        hat_summon = game_state.player1.summons.just_find(GrinMalkinHatSummon)
        self.assertEqual(hat_summon.usages, 1)
        self.assertEqual(p1_active_char(game_state).hp_lost(), 0)

    def test_prop_surplus_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = add_dmg_listener(game_state, Pid.P2)
        game_state = replace_character(game_state, Pid.P2, Lyney, char_id=1)
        game_state = grant_all_infinite_revival(game_state)
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget.from_player_active(game_state, Pid.P1),
            status=PropSurplusStatus(usages=2),
        ).execute(game_state)
        
        # check prop status cannot boost opponent damage
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL3)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 2)
        
        # check prop status cannot boost non-skill3 damage
        game_state = end_round(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 2)

        game_state = kill_character(game_state, char_id=2, pid=Pid.P1, hp=2)  # avoid self-damage
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 3)

        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIn(PropSurplusStatus, p1_active_char(game_state).character_statuses)
        prop_status = p1_active_char(game_state).character_statuses.just_find(PropSurplusStatus)
        self.assertEqual(prop_status.usages, 3)

        # check prop status can boost skill3 damage
        game_state = simulate_status_heal(game_state, 100, Pid.P1)
        game_state = simulate_status_dmg(game_state, 7, pid=Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 6)
        p1ac = p1_active_char(game_state)
        self.assertEqual(p1ac.hp_lost(), 4)
        self.assertNotIn(PropSurplusStatus, p1ac.character_statuses)
    
    def test_grin_malking_hat_summon(self):
        game_state = AddSummonEffect(Pid.P1, GrinMalkinHatSummon).execute(self.BASE_GAME)
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.PYRO)
        self.assertNotIn(GrinMalkinHatSummon, game_state.player1.summons)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = add_dmg_listener(game_state, Pid.P2)
        game_state = grant_all_infinite_revival(game_state)
        game_state = end_round(game_state, Pid.P2)

        # check no-boost when p2ac is not affected by Pyro
        assert not p2_active_char(game_state).elemental_aura.contains(Element.PYRO)
        game_state = simulate_status_dmg(game_state, 7, pid=Pid.P1)  # avoid self-damage
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ConclusiveOvation,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 3})),
        ))
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PYRO)
        
        # check boost when p2ac is affected by Pyro
        assert p2_active_char(game_state).elemental_aura.contains(Element.PYRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)

        # but once per round only
        assert p2_active_char(game_state).elemental_aura.contains(Element.PYRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)

        # summon not boosted because once per round
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)

        # opponent summon not boosted
        game_state = AddSummonEffect(Pid.P2, GrinMalkinHatSummon).execute(game_state)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 1)

        # self summon boosted
        game_state = AddSummonEffect(Pid.P1, GrinMalkinHatSummon).execute(game_state)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
