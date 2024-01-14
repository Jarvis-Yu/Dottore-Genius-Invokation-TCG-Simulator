import unittest

from .common_imports import *

class TestNatureAndWisdom(unittest.TestCase):
    def test_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            NatureAndWisdom: 1,
            SweetMadame: 4,
        }))
        base_state = replace_deck_cards(base_state, Pid.P1, Cards({
            SweetMadame: 1,
        }))

        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=NatureAndWisdom,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        about_to_select_state = game_state

        # check that card select phase is entered
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({
                SweetMadame: 5,
            }),
        )
        self.assertEqual(
            game_state.player1.deck_cards,
            Cards({}),
        )
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({
            MondstadtHashBrown: 2,
            MushroomPizza: 2,
            SweetMadame: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardsSelectAction(
            selected_cards=Cards({
                SweetMadame: 4,
            })
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({
                SweetMadame: 1,
                MondstadtHashBrown: 2,
                MushroomPizza: 2,
            }),
        )
        self.assertEqual(
            game_state.player1.deck_cards,
            Cards({
                SweetMadame: 5,
            }),
        )

        # check that card select phase is exited
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)  # no exception is succ

        # check that same cards may be selected if it have to be
        game_state = about_to_select_state
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({
            MondstadtHashBrown: 1,
            MushroomPizza: 1,
            SweetMadame: 1,
        }))
        game_state = step_action(game_state, Pid.P1, CardsSelectAction(
            selected_cards=Cards({
                SweetMadame: 4,
            })
        ))
        self.assertEqual(
            game_state.player1.hand_cards,
            Cards({
                SweetMadame: 3,
                MondstadtHashBrown: 1,
                MushroomPizza: 1,
            }),
        )
        self.assertEqual(
            game_state.player1.deck_cards,
            Cards({
                SweetMadame: 3,
            }),
        )

    def test_deck_validity(self):
        self.assertTrue(StoneAndContracts.valid_in_deck(MutableDeck(
            chars=[Keqing, Ningguang, Eula],
            cards={},
        )))
        self.assertFalse(StoneAndContracts.valid_in_deck(MutableDeck(
            chars=[Xingqiu, Nahida, Eula],
            cards={},
        )))
