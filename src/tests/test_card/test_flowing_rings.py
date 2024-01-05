import unittest

from .common_imports import *

class TestFlowingRings(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, FlowingRings).execute(base_state)
        base_state = grant_all_infinite_revival(base_state)

        # equip artifact
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FlowingRings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.OMNI: 0}),
            ),
        ))
        self.assertIn(FlowingRingsStatus, p1_active_char(game_state).character_statuses)

        # test elemental skill cannot draw card
        cards_before = game_state.player1.hand_cards.num_cards()
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), cards_before)

        # test normal attack can draw card
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), cards_before + 1)

        # test second normal attack cannot draw card in the same round
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), cards_before + 1)

        # test normal attack can draw card again in the next round
        game_state = next_round_with_great_omni(game_state)
        game_state = end_round(game_state, Pid.P2)
        cards_before = game_state.player1.hand_cards.num_cards()
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), cards_before + 1)
