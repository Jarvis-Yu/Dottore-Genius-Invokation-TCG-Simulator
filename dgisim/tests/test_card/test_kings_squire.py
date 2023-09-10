import unittest

from .common_imports import *

class TestKingsSquire(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, KingsSquire).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Fischl, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Ganyu, char_id=2)
        base_state = grant_all_infinite_revival(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = silent_fast_swap(base_state, Pid.P1, char_id=2)

        # equip amos bow for Fischl (off-field)
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=KingsSquire,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        # test Fischl's bow doesn't reduce cost for Ganyu
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDices(
            {Element.CRYO: 3}
        ))
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 1)
        self.assertIs(last_dmg.element, Element.CRYO)

        # equip for Ganyu
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=KingsSquire,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            )
        ))

        # test Elemental Skill now has cost reduction of 2 and dmg boosted by weapon
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDices(
            {Element.CRYO: 1}
        ))
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.CRYO)

        # test Fischl's Kings Squire effect is gone the next round
        game_state = step_swap(game_state, Pid.P1, char_id=1)
        game_state = next_round_with_great_omni(game_state)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDices(
            {Element.ELECTRO: 3}
        ))
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.ELECTRO)
