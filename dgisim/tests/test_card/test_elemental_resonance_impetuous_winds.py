import unittest

from .common_imports import *


class TestElementalImpetuousWinds(unittest.TestCase):
    BASE_GAME = PublicAddCardEffect(
        Pid.P1, card=ElementalResonanceImpetuousWinds,
    ).execute(ACTION_TEMPLATE)

    def test_card_in_deck(self):
        self.assertFalse(
            ElementalResonanceImpetuousWinds.valid_in_deck(
                MutableDeck(chars=[Venti, Bennett, YaeMiko], cards={})
            )
        )
        self.assertTrue(
            ElementalResonanceImpetuousWinds.valid_in_deck(
                MutableDeck(chars=[Bennett, Venti, KaedeharaKazuha], cards={})
            )
        )

    def test_status_behaviour(self):
        base_state = self.BASE_GAME
        for i in range(3):
            base_state = PublicAddCardEffect(
                Pid.P1, ElementalResonanceImpetuousWinds
            ).execute(base_state)

        self.assertTrue(ElementalResonanceImpetuousWinds.strictly_usable(base_state, Pid.P1))
        old_dices = base_state.get_player1().get_dices()
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=ElementalResonanceImpetuousWinds,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dices=ActualDices({Element.ANEMO: 1}),
            )
        ))
        p1ac = game_state.get_player1().just_get_active_character()
        p1_dices = game_state.get_player1().get_dices()
        self.assertEqual(p1ac.get_id(), 2)
        self.assertIs(game_state.get_active_player_id(), Pid.P1)
        self.assertEqual(p1_dices[Element.ANEMO] + 1, old_dices[Element.ANEMO])
        self.assertEqual(p1_dices[Element.OMNI] - 1, old_dices[Element.OMNI])

        game_state = kill_character(game_state, 1, Pid.P1)
        self.assertTrue(ElementalResonanceImpetuousWinds.strictly_usable(game_state, Pid.P1))
        old_dices = game_state.get_player1().get_dices()
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=ElementalResonanceImpetuousWinds,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dices=ActualDices({Element.OMNI: 1}),
            )
        ))
        p1ac = game_state.get_player1().just_get_active_character()
        p1_dices = game_state.get_player1().get_dices()
        self.assertEqual(p1ac.get_id(), 3)
        self.assertIs(game_state.get_active_player_id(), Pid.P1)
        self.assertEqual(p1_dices[Element.ANEMO], old_dices[Element.ANEMO])
        self.assertEqual(p1_dices[Element.OMNI], old_dices[Element.OMNI])

        game_state = kill_character(game_state, 2, Pid.P1)
        self.assertFalse(ElementalResonanceImpetuousWinds.strictly_usable(game_state, Pid.P1))