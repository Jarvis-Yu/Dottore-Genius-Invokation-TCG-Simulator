import unittest

from src.tests.test_characters.common_imports import *


class TestCollei(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Collei,
        char_id=2,
        card=FloralSidewinder,
    )
    assert type(BASE_GAME.get_player1().just_get_active_character()) is Collei

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.DENDRO: 1, Element.HYDRO: 1, Element.GEO: 1}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertFalse(p2ac.get_elemental_aura().has_aura())

    def test_elemental_skill1(self):
        # test elemental skill deals 3 dendro damage
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.DENDRO: 3}),
        )
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            dice=ActualDice({Element.DENDRO: 3}),
        )
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertIn(CuileinAnbarSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(CuileinAnbarSummon).usages, 2)

    def test_cuilein_anbar_summon(self):
        game_state = AddSummonEffect(Pid.P1, CuileinAnbarSummon).execute(self.BASE_GAME)
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 8)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertIn(CuileinAnbarSummon, p1.get_summons())
        self.assertEqual(p1.get_summons().just_find(CuileinAnbarSummon).usages, 1)

        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertNotIn(CuileinAnbarSummon, p1.get_summons())

    def test_talent_card_and_sprout_status(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=FloralSidewinder,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 4}))
        ))
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 7)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertIn(SproutStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(SproutStatus).usages, 1)

        # dendro reaction from teammate triggers sprout status
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=3)
        assert isinstance(game_state.get_player1().just_get_active_character(), Keqing)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 1)  # damage = 6 = 4 + 2
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertNotIn(SproutStatus, p1.get_combat_statuses())

        # second talent card in same round doesn't generate another sprout status
        game_state = heal_for_all(game_state)
        game_state = apply_elemental_aura(game_state, Element.ELECTRO, Pid.P2)
        game_state = PublicAddCardEffect(Pid.P1, FloralSidewinder).execute(game_state)
        game_state = skip_action_round(game_state, Pid.P2)
        game_state = silent_fast_swap(game_state, Pid.P1, char_id=2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FloralSidewinder,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 4}))
        ))
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 6)  # damage = 4 = 3 + 1  (from catalyzing field)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertNotIn(SproutStatus, p1.get_combat_statuses())

        # elemental skill next round generates sprout status again
        game_state = heal_for_all(game_state)
        game_state = next_round(game_state)
        game_state = fill_dice_with_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        p1 = game_state.get_player1()
        self.assertIn(SproutStatus, p1.get_combat_statuses())
        self.assertEqual(p1.get_combat_statuses().just_find(SproutStatus).usages, 1)

        # on-skill dendro reaction triggers sprout status immediately
        game_state = apply_elemental_aura(self.BASE_GAME, Element.ELECTRO, Pid.P2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=FloralSidewinder,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 4}))
        ))
        p1 = game_state.get_player1()
        p2ac = game_state.get_player2().just_get_active_character()
        self.assertEqual(p2ac.get_hp(), 4)
        self.assertIn(Element.DENDRO, p2ac.get_elemental_aura())
        self.assertNotIn(SproutStatus, p1.get_combat_statuses())

        # sprout status disappears naturally next round
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=FloralSidewinder,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.DENDRO: 4}))
        ))
        game_state = next_round(game_state)
        p1 = game_state.get_player1()
        self.assertNotIn(SproutStatus, p1.get_combat_statuses())
