import unittest

from .common_imports import *


class TestNRE(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = base_state.factory().f_player1(
            lambda p1: p1.factory().deck_cards(
                Cards.from_empty().add(SweetMadame).add(SweetMadame)
            ).build()
        ).build()
        base_state = PublicAddCardEffect(Pid.P1, NRE).execute(base_state)
        for i in range(2):
            base_state = PublicAddCardEffect(Pid.P1, NorthernSmokedChicken).execute(base_state)

        # test food added on entry
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=NRE,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.PYRO: 1, Element.GEO: 1})),
        ))
        deck_cards = game_state.get_player1().get_deck_cards()
        hand_cards = game_state.get_player1().get_hand_cards()
        self.assertEqual(deck_cards[SweetMadame], 1)
        self.assertEqual(hand_cards[SweetMadame], 1)
        nre_played_state = game_state

        # test food added on playing food
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            ),
        ))
        deck_cards = game_state.get_player1().get_deck_cards()
        hand_cards = game_state.get_player1().get_hand_cards()
        self.assertEqual(deck_cards[SweetMadame], 0)
        self.assertEqual(hand_cards[SweetMadame], 2)

        # test food addition can only be triggered once per round
        game_state = game_state.factory().f_player1(
            lambda p1: p1.factory().f_deck_cards(
                lambda cds: cds.add(MondstadtHashBrown)
            ).build()
        ).build()
        with_food_state = game_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            ),
        ))
        deck_cards = game_state.get_player1().get_deck_cards()
        hand_cards = game_state.get_player1().get_hand_cards()
        self.assertEqual(deck_cards[MondstadtHashBrown], 1)
        self.assertEqual(hand_cards[MondstadtHashBrown], 0)


        # test no food in deck still consumes the usages
        game_state = nre_played_state.factory().f_player1(
            lambda p1: p1.factory().f_deck_cards(
                lambda cds: cds.remove(SweetMadame)
            ).build()
        ).build()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 1),
            ),
        ))
        game_state = game_state.factory().f_player1(
            lambda p1: p1.factory().f_deck_cards(
                lambda cds: cds.add(MondstadtHashBrown)
            ).build()
        ).build()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            ),
        ))
        deck_cards = game_state.get_player1().get_deck_cards()
        hand_cards = game_state.get_player1().get_hand_cards()
        self.assertEqual(deck_cards[MondstadtHashBrown], 1)
        self.assertEqual(hand_cards[MondstadtHashBrown], 0)

        # test usages refresh the next round
        game_state = with_food_state
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dice=ActualDice.from_empty(),
                target=StaticTarget.from_char_id(Pid.P1, 2),
            ),
        ))
        deck_cards = game_state.get_player1().get_deck_cards()
        hand_cards = game_state.get_player1().get_hand_cards()
        self.assertEqual(deck_cards[MondstadtHashBrown], 0)
        self.assertEqual(hand_cards[MondstadtHashBrown], 1)