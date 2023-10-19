import unittest

from .common_imports import *


class TestSendOff(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SendOff: 10,
        }))
        base_state = AddSummonEffect(Pid.P2, ReflectionSummon).execute(base_state)
        base_state = AddSummonEffect(Pid.P2, BurningFlameSummon).execute(base_state)
        base_state = AddSummonEffect(Pid.P2, SesshouSakuraSummon).execute(base_state)
        base_state = AddSummonEffect(Pid.P2, OceanicMimicFrogSummon).execute(base_state)

        # test cannot remove Mona's summon - Reflection Summon
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SendOff,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.ANEMO: 1, Element.DENDRO: 1}),
                target=StaticTarget.from_summon(Pid.P2, ReflectionSummon),
            ),
        ))
        p2_summons = game_state.get_player2().get_summons()
        self.assertIn(ReflectionSummon, p2_summons)
        summon = p2_summons.just_find(ReflectionSummon)
        self.assertEqual(summon.usages, 0)

        # test can remove burning summon
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SendOff,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.HYDRO: 1, Element.ELECTRO: 1}),
                target=StaticTarget.from_summon(Pid.P2, BurningFlameSummon),
            ),
        ))
        p2_summons = game_state.get_player2().get_summons()
        self.assertNotIn(BurningFlameSummon, p2_summons)

        # test can properly remove Sesshou Sakura Summon
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SendOff,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.GEO: 1, Element.PYRO: 1}),
                target=StaticTarget.from_summon(Pid.P2, SesshouSakuraSummon),
            ),
        ))
        p2_summons = game_state.get_player2().get_summons()
        self.assertIn(SesshouSakuraSummon, p2_summons)
        summon = p2_summons.just_find(SesshouSakuraSummon)
        self.assertEqual(summon.usages, 1)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SendOff,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.CRYO: 2}),
                target=StaticTarget.from_summon(Pid.P2, SesshouSakuraSummon),
            ),
        ))
        p2_summons = game_state.get_player2().get_summons()
        self.assertNotIn(SesshouSakuraSummon, p2_summons)

        # test on Rhodeia's Frog Summon cannot be removed
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SendOff,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.GEO: 1, Element.PYRO: 1}),
                target=StaticTarget.from_summon(Pid.P2, OceanicMimicFrogSummon),
            ),
        ))
        p2_summons = game_state.get_player2().get_summons()
        self.assertIn(OceanicMimicFrogSummon, p2_summons)
        summon = p2_summons.just_find(OceanicMimicFrogSummon)
        self.assertEqual(summon.usages, 0)
