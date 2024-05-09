import unittest

from src.tests.test_characters.common_imports import *


class TestYelan(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Yelan,
        char_id=2,
        card=TurnControl,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.HYDRO: 1, Element.PYRO: 1, Element.CRYO: 1}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)

        old_breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        assert old_breakthrough.usages == 1
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.HYDRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.HYDRO)
        new_breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(new_breakthrough.usages, 3)

    def test_elemental_burst(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = recharge_energy_for_all(game_state)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.HYDRO: 3}),
        )
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 3)
        self.assertIs(dmg.element, Element.HYDRO)
        self.assertIn(ExquisiteThrowStatus, game_state.player1.combat_statuses)
        exquisite_throw = game_state.player1.combat_statuses.just_find(ExquisiteThrowStatus)
        self.assertEqual(exquisite_throw.usages, 2)

    def test_break_through_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = end_round(game_state, Pid.P2)
        game_state = grant_all_infinite_revival(game_state)
        game_state = replace_deck_cards(game_state, Pid.P1, Cards({Paimon: 5}))
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({}))

        # check breakthrough(1) has no effect
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.PHYSICAL)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 0)

        # check breakthrough(2) makes normal attack hydro and draws a card
        game_state = OverrideCharacterStatusEffect(
            StaticTarget.from_player_active(game_state, Pid.P1),
            BreakthroughStatus(usages=2),
        ).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.HYDRO)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 1)
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 0)

        # check breakthrough(3) makes normal attack hydro and draws a card (consume 2 usages only)
        game_state = OverrideCharacterStatusEffect(
            StaticTarget.from_player_active(game_state, Pid.P1),
            BreakthroughStatus(usages=3),
        ).execute(game_state)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmg = get_dmg_listener_data(game_state, Pid.P1)[-1]
        self.assertEqual(dmg.damage, 2)
        self.assertIs(dmg.element, Element.HYDRO)
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 2)
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 1)

    def test_exquisite_throw_status(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = end_round(game_state, Pid.P2)
        game_state = grant_all_infinite_revival(game_state)
        game_state = AddCombatStatusEffect(Pid.P1, ExquisiteThrowStatus).execute(game_state)

        # check exquisite throw follow up all normal attack
        game_state = replace_character(game_state, Pid.P1, Ganyu, char_id=1)
        game_state = silent_fast_swap(game_state, Pid.P1, 1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 2)
        _, follow_up = dmgs
        self.assertEqual(follow_up.damage, 1)
        self.assertIs(follow_up.element, Element.HYDRO)

        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 1)

        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL3)
        dmgs = get_dmg_listener_data(game_state, Pid.P1)
        self.assertEqual(len(dmgs), 4)
        _, _, _, follow_up = dmgs
        self.assertEqual(follow_up.damage, 2)  # 1 from exquisite throw, 1 from freeze reaction
        self.assertIs(follow_up.element, Element.HYDRO)

        # check usages decrease at end round
        exquisite_throw = game_state.player1.combat_statuses.just_find(ExquisiteThrowStatus)
        self.assertEqual(exquisite_throw.usages, 2)
        game_state = next_round(game_state)
        exquisite_throw = game_state.player1.combat_statuses.just_find(ExquisiteThrowStatus)
        self.assertEqual(exquisite_throw.usages, 1)
        game_state = next_round(game_state)
        self.assertNotIn(ExquisiteThrowStatus, game_state.player1.combat_statuses)

    def test_passive(self):
        # checks passive increase breakthrough usages at end-round
        game_state = self.BASE_GAME
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 1)

        game_state = next_round(game_state)
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 2)

        game_state = next_round(game_state)
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 3)

        game_state = next_round(game_state)
        breakthrough = p1_active_char(game_state).character_statuses.just_find(BreakthroughStatus)
        self.assertEqual(breakthrough.usages, 3)

    def test_talent_card(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TurnControl,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.HYDRO: 3})),
        ))

        # check dice reroll condition
        ## Mono Element ##
        game_state = replace_character(game_state, Pid.P1, SangonomiyaKokomi, 1)
        game_state = replace_character(game_state, Pid.P1, Mona, 3)
        game_state = next_round(game_state)
        self.assertGreaterEqual(game_state.player1.dice[Element.OMNI], 1)

        ## Duo Element ##
        game_state = replace_character(game_state, Pid.P1, Bennett, 1)
        game_state = replace_character(game_state, Pid.P1, Mona, 3)
        game_state = next_round(game_state)
        self.assertGreaterEqual(game_state.player1.dice[Element.OMNI], 2)

        ## Duo Element ##
        game_state = replace_character(game_state, Pid.P1, Bennett, 1)
        game_state = replace_character(game_state, Pid.P1, YaeMiko, 3)
        game_state = next_round(game_state)
        self.assertGreaterEqual(game_state.player1.dice[Element.OMNI], 3)
