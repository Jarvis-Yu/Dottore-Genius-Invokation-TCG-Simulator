import unittest

from .common_imports import *

class TestGuardiansOath(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            GuardiansOath: 2,
        }))

        game_state = base_state

        # test that it can be played with no summon on field
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GuardiansOath,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 4})),
        ))

        # test that it removes all summons (self and opponent's)
        game_state = AddSummonEffect(Pid.P1, OceanicMimicFrogSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, LightfallSwordSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, FierySanctumFieldSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P1, BurningFlameSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P2, OzSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P2, SacredCryoPearlSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P2, ClusterbloomArrowSummon).execute(game_state)
        game_state = AddSummonEffect(Pid.P2, UshiSummon).execute(game_state)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GuardiansOath,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 4})),
        ))

        p1_summons = game_state.player1.summons
        p2_summons = game_state.player2.summons
        self.assertEqual(len(p1_summons), 0)
        self.assertEqual(len(p2_summons), 0)
