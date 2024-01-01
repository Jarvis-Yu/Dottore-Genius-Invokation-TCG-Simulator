import unittest

from .common_imports import *

class TestElegyForTheEnd(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, ElegyForTheEnd).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Venti, 1)
        base_state = replace_character(base_state, Pid.P1, Yoimiya, 2)
        base_state = replace_character(base_state, Pid.P1, Ganyu, 3)
        base_state = replace_character(base_state, Pid.P2, Venti, 1)
        base_state = grant_all_infinite_revival(base_state)

        # equip weapon
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElegyForTheEnd,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 3}),
            ),
        ))
        self.assertIn(ElegyForTheEndStatus, p1_active_char(game_state).get_character_statuses())

        # test normal attack deals +1 dmg
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.PHYSICAL)

        # test opponent's normal attack keeps the same
        game_state = add_dmg_listener(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

        # test brust triggers weapon
        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1 = game_state.get_player1()
        self.assertIn(MillennialMovementFarewellSongStatus, p1.get_combat_statuses())
        self.assertEqual(
            p1.get_combat_statuses().just_find(MillennialMovementFarewellSongStatus).usages,
            2,
        )
        
        # test generated status boosts team dmg by 1
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 4)  # base 2 + weapon 1 + status 1
        self.assertIs(dmg.element, Element.PHYSICAL)

        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)  # base 2 + status 1
        self.assertIs(dmg.element, Element.PHYSICAL)

        # test opponent dmg keeps the same
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P2)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

        # test summon doesn't get boosts and millennial... status usages - 1
        game_state = AddSummonEffect(Pid.P1, OzSummon).execute(game_state)
        game_state = next_round(game_state)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 1)
        self.assertIs(dmg.element, Element.ELECTRO)
        p1 = game_state.get_player1()
        self.assertIn(MillennialMovementFarewellSongStatus, p1.get_combat_statuses())
        self.assertEqual(
            p1.get_combat_statuses().just_find(MillennialMovementFarewellSongStatus).usages,
            1,
        )
