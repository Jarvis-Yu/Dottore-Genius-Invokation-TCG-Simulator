import unittest

from .common_imports import *

SUPPORT = CentralLaboratoryRuins
SUPPORT_STATUS = CentralLaboratoryRuinsSupport

def p1_support_status(game_state: GameState, sid: int = 1) -> SUPPORT_STATUS:
    return game_state.player1.supports.just_find(SUPPORT_STATUS, sid)

class TestCentralLaboratoryRuins(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SUPPORT: 1,
            TaroumarusSavings: 9,
        }))
        base_state = replace_hand_cards(base_state, Pid.P2, Cards({TaroumarusSavings: 10}))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({TaroumarusSavings: 30}))
        base_state = play_support_card(base_state, Pid.P1, SUPPORT, cost=1)
        base_state = replace_character(base_state, Pid.P1, Xinyan, 1)
        base_state = replace_character(base_state, Pid.P1, Kaveh, 2)
        base_state = replace_character(base_state, Pid.P1, Ningguang, 3)
        base_state = replace_character(base_state, Pid.P2, Bennett, 1)
        base_state = grant_all_infinite_revival(base_state)
        self.assertEqual(p1_support_status(base_state, 1).usages, 0)

        # check playing card does not trigger lab
        game_state = base_state
        game_state = play_dice_only_card(game_state, Pid.P1, TaroumarusSavings)
        self.assertEqual(p1_support_status(game_state, 1).usages, 0)

        omni_num = game_state.player1.dice[Element.OMNI]

        # check tuning triggers
        game_state = tune_elem(game_state, Pid.P1, Element.ELECTRO, TaroumarusSavings)
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num)

        # check oppo tuning doesn't trigger
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = tune_elem(game_state, Pid.P2, Element.ELECTRO, TaroumarusSavings)
        self.assertEqual(p1_support_status(game_state, 1).usages, 1)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num)
        game_state = end_round(game_state, Pid.P2)

        # check discarding deck card triggers
        game_state = add_combat_status(game_state, Pid.P1, BurstScanStatus)
        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = add_combat_status(game_state, Pid.P1, ChangingShiftsStatus)
        game_state = step_swap(game_state, Pid.P1, 1, cost=0)
        self.assertEqual(p1_support_status(game_state, 1).usages, 2)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num)

        # check reaching 3 gives one OMNI
        game_state = add_combat_status(game_state, Pid.P1, BurstScanStatus)
        game_state = apply_elemental_aura(game_state, Element.DENDRO, Pid.P2)
        game_state = apply_elemental_aura(game_state, Element.HYDRO, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, 2)
        game_state = add_combat_status(game_state, Pid.P1, ChangingShiftsStatus)
        game_state = step_swap(game_state, Pid.P1, 1, cost=0)
        self.assertEqual(p1_support_status(game_state, 1).usages, 3)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num + 1)

        # check direct discard triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.PYRO: 3}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 4)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num + 1)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.PYRO: 3}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 5)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num + 1)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, cost=ActualDice({Element.PYRO: 3}))
        self.assertEqual(p1_support_status(game_state, 1).usages, 6)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num + 2)

        # check Xinyan burst
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Paimon: 3}))
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.PYRO: 3}))
        self.assertNotIn(SUPPORT_STATUS, game_state.player1.supports)
        self.assertEqual(game_state.player1.dice[Element.OMNI], omni_num + 3)
