import unittest

from .common_imports import *


class TestTandooriRoastChicken(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TandooriRoastChicken: 2,
            LotusFlowerCrisp: 1,
        }))
        base_state = replace_character(base_state, Pid.P1, Collei, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Nahida, char_id=2)
        base_state = replace_character(base_state, Pid.P1, JadeplumeTerrorshroom, char_id=3)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=LotusFlowerCrisp,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.CRYO: 1}),
                target=StaticTarget.from_char_id(Pid.P1, char_id=2),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TandooriRoastChicken,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.CRYO: 1, Element.GEO: 1})),
        ))

        # test tandoori applies to un-satiated chars and can be triggered once only by elemental skill
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)

        game_state = fill_energy_for_all(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)

        game_state = step_swap(game_state, Pid.P1, char_id=2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)

        game_state = step_swap(game_state, Pid.P1, char_id=3)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 5)

        # test status last only one round
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TandooriRoastChicken,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 1, Element.HYDRO: 1})),
        ))
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)