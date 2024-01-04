import unittest

from .common_imports import *

class TestFavoniusSword(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for _ in range(3):
            base_state = PublicAddCardEffect(Pid.P1, FavoniusSword).execute(base_state)

        base_state = replace_character(base_state, Pid.P1, Keqing, char_id=1)
        base_state = silent_fast_swap(base_state, Pid.P1, char_id=1)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FavoniusSword,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        # normal attack doesn't trigger
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertEqual(p1_active_char(game_state).energy, 1)

        # burst doesn't trigger
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        self.assertEqual(p1_active_char(game_state).energy, 0)

        # elemental skill triggers
        game_state = drain_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 2)

        # can only be triggered once per round
        game_state = drain_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 1)

        # if replaced, then can be triggered again
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FavoniusSword,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = drain_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 2)

        # usages refresh next round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = drain_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(p1_active_char(game_state).energy, 2)
