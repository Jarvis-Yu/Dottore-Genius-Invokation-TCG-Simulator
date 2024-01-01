import unittest

from .common_imports import *

class TestFruitOfFullfillment(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, FruitOfFulfillment).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Klee, char_id=1)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # equip amos bow for Fischl (off-field)
        deck_cards_before = base_state.player1.deck_cards
        hand_cards_before = base_state.player1.hand_cards
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=FruitOfFulfillment,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.GEO: 1, Element.ELECTRO: 1, Element.ANEMO: 1}),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            )
        ))
        deck_cards_after = game_state.player1.deck_cards
        hand_cards_after = game_state.player1.hand_cards
        self.assertEqual(deck_cards_after.num_cards(), deck_cards_before.num_cards() - 2)
        self.assertEqual(hand_cards_after.num_cards(), hand_cards_before.num_cards() + 1)
        self.assertEqual(
            hand_cards_after + deck_cards_after + {FruitOfFulfillment: 1},
            hand_cards_before + deck_cards_before
        )

        # test basic dmg boost
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1, ActualDice(
            {Element.PYRO: 3}
        ))
        last_dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(last_dmg.damage, 2)
        self.assertIs(last_dmg.element, Element.PYRO)