import unittest

from .common_imports import *

class TestEngulfingLightning(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, EngulfingLightning).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, HuTao, char_id=1)
        base_state = silent_fast_swap(base_state, Pid.P1, char_id=1)
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=EngulfingLightning,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        # check that recharge triggered on equipment
        p1ac = p1_active_char(game_state)
        self.assertEqual(p1ac.energy, 1)

        # check that can only be triggered once per round
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        p1ac = p1_active_char(game_state)
        self.assertEqual(p1ac.energy, 0)
        game_state = drain_energy_for_all(game_state)

        # check that can be triggered again at the start of next round
        game_state = next_round_with_great_omni(game_state)
        p1ac = p1_active_char(game_state)
        self.assertEqual(p1ac.energy, 1)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)

        # check that Calx's Art can trigger
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        game_state = PublicAddCardEffect(Pid.P1, CalxsArts).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=CalxsArts,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1})),
        ))
        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.energy, 1)
        self.assertEqual(p1c2.energy, 1)
