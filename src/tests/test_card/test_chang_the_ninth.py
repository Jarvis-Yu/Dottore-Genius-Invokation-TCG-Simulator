import unittest

from .common_imports import *


class TestChangTheNinth(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, ChangTheNinth).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Keqing, char_id=1)
        base_state = replace_character(base_state, Pid.P2, Xingqiu, char_id=1)
        base_state = grant_all_infinite_revival(base_state)

        # use the support card
        game_state = step_action(base_state, Pid.P1, CardAction(
            card=ChangTheNinth,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))

        def get_chang(game_state: GameState) -> ChangTheNinthSupport:
            chang = game_state.get_player1().get_supports().find(ChangTheNinthSupport, 1)
            self.assertIsNotNone(chang)
            assert isinstance(chang, ChangTheNinthSupport)
            return chang

        chang = get_chang(game_state)
        self.assertEqual(chang.usages, 0)

        # test physical dmg triggers
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        self.assertEqual(get_chang(game_state).usages, 1)

        game_state_1 = game_state

        # test reaction (applied reaction) triggers
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)
        self.assertEqual(get_chang(game_state).usages, 2)

        # test summon cannot trigger
        game_state = AddSummonEffect(Pid.P1, OceanicMimicRaptorSummon).execute(game_state)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P2)
        game_state = next_round_with_great_omni(game_state)
        self.assertEqual(get_chang(game_state).usages, 2)
        game_state = skip_action_round_until(game_state, Pid.P1)
        assert not game_state.get_player2().just_get_active_character().get_elemental_aura().has_aura()
        game_state = replace_character(game_state, Pid.P1, Ganyu, char_id=1)
        old_deck_cards = game_state.get_player1().get_deck_cards()
        old_hand_cards = game_state.get_player1().get_hand_cards()
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        new_deck_cards = game_state.get_player1().get_deck_cards()
        new_hand_cards = game_state.get_player1().get_hand_cards()
        optional_chang = game_state.get_player1().get_supports().find(ChangTheNinthSupport, 1)
        self.assertIsNone(optional_chang)
        self.assertEqual(new_hand_cards + new_deck_cards, old_hand_cards + old_deck_cards)
        self.assertEqual(new_hand_cards.num_cards(), old_hand_cards.num_cards() + 2)
