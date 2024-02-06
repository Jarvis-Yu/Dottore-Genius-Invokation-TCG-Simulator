import unittest

from src.tests.test_characters.common_imports import *


class TestLisa(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ONE_ACTION_TEMPLATE,
        Pid.P1,
        Lisa,
        char_id=2,
        card=PulsatingWitch,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        
        # no charge
        game_state = replace_dice(game_state, Pid.P1, ActualDice({
            Element.OMNI: 11,
        }))
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ELECTRO)
        p2ac = p2_active_char(game_state)
        self.assertNotIn(ConductiveStatus, p2ac.character_statuses)

        # charged
        game_state = replace_dice(game_state, Pid.P1, ActualDice({
            Element.OMNI: 10,
        }))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ELECTRO)
        p2ac = p2_active_char(game_state)
        self.assertIn(ConductiveStatus, p2ac.character_statuses)
        conductive_status = p2ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 2)

        # recreation of status only gives 1 more usage
        game_state = replace_dice(game_state, Pid.P1, ActualDice({
            Element.OMNI: 10,
        }))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p2ac = p2_active_char(game_state)
        self.assertIn(ConductiveStatus, p2ac.character_statuses)
        conductive_status = p2ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 3)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = grant_all_infinite_revival(game_state)
        
        # add conductive status when not present
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ELECTRO)
        p2c1, _, _ = p2_chars(game_state)
        self.assertIn(ConductiveStatus, p2c1.character_statuses)

        # deals more damage when conductive status is present
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)
        self.assertIs(dmg.element, Element.ELECTRO)
        p2c1, _, _ = p2_chars(game_state)
        self.assertNotIn(ConductiveStatus, p2c1.character_statuses)

        # overload adds conductive to the at-the-moment active character
        game_state = remove_aura(game_state, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p2c1, p2c2, _ = p2_chars(game_state)
        self.assertNotIn(ConductiveStatus, p2c1.character_statuses)
        self.assertIn(ConductiveStatus, p2c2.character_statuses)

        # boosted skill don't apply conductive even if overloaded
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        _, p2c2, p2c3 = p2_chars(game_state)
        self.assertNotIn(ConductiveStatus, p2c2.character_statuses)
        self.assertNotIn(ConductiveStatus, p2c3.character_statuses)

    def test_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.ELECTRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ELECTRO)
        self.assertIn(LightningRoseSummon, game_state.player1.summons)

    def test_conductive_status(self):
        game_state = RelativeAddCharacterStatusEffect(
            source_pid=Pid.P1,
            target=DynamicCharacterTarget.SELF_ACTIVE,
            status=ConductiveStatus,
        ).execute(self.BASE_GAME)
        p1ac = p1_active_char(game_state)
        self.assertIn(ConductiveStatus, p1ac.character_statuses)
        conductive_status = p1ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 2)

        # usages increase automatically each round
        game_state = next_round(game_state)
        p1ac = p1_active_char(game_state)
        self.assertIn(ConductiveStatus, p1ac.character_statuses)
        conductive_status = p1ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 3)

        # and so on, but cap at 4
        game_state = next_round(game_state)
        p1ac = p1_active_char(game_state)
        self.assertIn(ConductiveStatus, p1ac.character_statuses)
        conductive_status = p1ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 4)

        game_state = next_round(game_state)
        p1ac = p1_active_char(game_state)
        self.assertIn(ConductiveStatus, p1ac.character_statuses)
        conductive_status = p1ac.character_statuses.just_find(ConductiveStatus)
        self.assertEqual(conductive_status.usages, 4)

    def test_lightning_rose_summon(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_stae = grant_all_infinite_revival(game_state)
        game_state = AddSummonEffect(Pid.P1, LightningRoseSummon).execute(game_state)
        summon = game_state.player1.summons.just_find(LightningRoseSummon)
        self.assertEqual(summon.usages, 2)

        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ELECTRO)
        summon = game_state.player1.summons.just_find(LightningRoseSummon)
        self.assertEqual(summon.usages, 1)

        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.ELECTRO)
        self.assertNotIn(LightningRoseSummon, game_state.player1.summons)

    def test_talent_card(self):
        game_state = self.BASE_GAME
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=PulsatingWitch,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        p1ac = p1_active_char(game_state)
        self.assertIn(PulsatingWitchStatus, p1ac.character_statuses)
        p2ac = p2_active_char(game_state)
        self.assertNotIn(ConductiveStatus, p2ac.character_statuses)

        game_state = step_swap(game_state, Pid.P1, 3)
        p2ac = p2_active_char(game_state)
        self.assertNotIn(ConductiveStatus, p2ac.character_statuses)

        # swapping to lisa adds conductive status to opponent
        game_state = step_swap(game_state, Pid.P1, 2)
        p2ac = p2_active_char(game_state)
        self.assertIn(ConductiveStatus, p2ac.character_statuses)

        # once per round
        game_state = silent_fast_swap(game_state, Pid.P2, 2)
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_swap(game_state, Pid.P1, 2)
        p2ac = p2_active_char(game_state)
        self.assertNotIn(ConductiveStatus, p2ac.character_statuses)

        # refreshes the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = step_swap(game_state, Pid.P1, 3)
        game_state = step_swap(game_state, Pid.P1, 2)
        p2ac = p2_active_char(game_state)
        self.assertIn(ConductiveStatus, p2ac.character_statuses)
