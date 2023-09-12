import unittest

from .common_imports import *

class TestWhereIsTheUnseenRazor(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, WhereIsTheUnseenRazor).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P1, RavenBow).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Fischl, char_id=1)
        base_state = grant_all_infinite_revival(base_state)

        # equip bow for Fischl
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=RavenBow,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 2}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        self.assertNotIn(RavenBow, game_state.get_player1().get_hand_cards())

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=WhereIsTheUnseenRazor,
            instruction=StaticTargetInstruction(
                dices=ActualDices.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))

        self.assertIn(RavenBow, game_state.get_player1().get_hand_cards())

        # test use with King's Squire
        game_state = PublicAddCardEffect(Pid.P1, KingsSquire).execute(base_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=KingsSquire,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 3}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDices(
            {Element.ELECTRO: 1}
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=WhereIsTheUnseenRazor,
            instruction=StaticTargetInstruction(
                dices=ActualDices.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=KingsSquire,
            instruction=StaticTargetInstruction(
                dices=ActualDices({Element.PYRO: 1}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2, ActualDices(
            {Element.ELECTRO: 1}
        ))