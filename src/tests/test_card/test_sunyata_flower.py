import unittest

from .common_imports import *

class TestTheBoarPrincess(unittest.TestCase):
    def test_substitute_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            SunyataFlower: 1,
        }))

        game_state = base_state

        # check cannot be played without support
        self.assertFalse(SunyataFlower.loosely_usable(game_state, Pid.P1))

        # check adds the right status and adds two support cards
        game_state = AddSupportEffect(Pid.P1, LibenSupport).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SunyataFlower,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_support(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))

        self.assertNotIn(LibenSupport, game_state.player1.supports)
        hand_cards = game_state.player1.hand_cards
        self.assertEqual(hand_cards.num_cards(), 2)
        self.assertTrue(all(
            issubclass(card, SupportCard)
            for card in hand_cards
        ), hand_cards)
        self.assertIn(SunyataFlowerStatus, game_state.player1.combat_statuses)

    def test_sunyata_flower_status(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            Paimon: 1,
        }))
        base_state = AddCombatStatusEffect(Pid.P1, SunyataFlowerStatus).execute(base_state)

        game_state = base_state

        # check that the status has 1 cost deduction for support cards
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=Paimon,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 2})),
        ))
        self.assertNotIn(SunyataFlowerStatus, game_state.player1.combat_statuses)

        # check that status is removed after the current round
        game_state = AddCombatStatusEffect(Pid.P1, SunyataFlowerStatus).execute(game_state)
        game_state = next_round(game_state)
        self.assertNotIn(SunyataFlowerStatus, game_state.player1.combat_statuses)
