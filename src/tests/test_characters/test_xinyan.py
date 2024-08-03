import random
import unittest

from src.tests.test_characters.common_imports import *


class TestXinyan(unittest.TestCase):
    BASE_GAME = replace_character_make_active_add_card(
        ACTION_TEMPLATE,
        Pid.P1,
        Xinyan,
        char_id=2,
        card=RockinInAFlamingWorld,
    )

    def test_skill1(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL1,
            cost=ActualDice({Element.PYRO: 1, Element.CRYO: 1, Element.GEO: 1}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PHYSICAL)

    def test_skill2(self):
        game_state = add_dmg_listener(self.BASE_GAME, Pid.P1)
        hands = Cards({
            GamblersEarrings: 2,  # 1
            Strategize: 2,  # 1
            GeneralsAncientHelm: 2,  # 2
            TravelersHandySword: 2,  # 2
            Paimon: 2,  # 3
            TenacityOfTheMillelith: 2,  # 3
        })
        game_state = replace_hand_cards(game_state, Pid.P1, hands)
        assert GamblersEarrings._DICE_COST.num_dice() == 1
        assert Strategize._DICE_COST.num_dice() == 1
        assert GeneralsAncientHelm._DICE_COST.num_dice() == 2
        assert TravelersHandySword._DICE_COST.num_dice() == 2
        assert Paimon._DICE_COST.num_dice() == 3
        assert TenacityOfTheMillelith._DICE_COST.num_dice() == 3

        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.SKILL2,
            cost=ActualDice({Element.PYRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elem=Element.PYRO)
        self.assertIn(ShieldOfPassionStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ShieldOfPassionStatus).usages, 2)
        self.assertTrue(
            game_state.player1.hand_cards == hands - {Paimon: 1}
            or game_state.player1.hand_cards == hands - {TenacityOfTheMillelith: 1}
        )

    def test_elemental_burst(self):
        game_state = self.BASE_GAME
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({
            card: random.randint(1, 2)
            for card in random.choices(list(game_state.mode.all_cards()), k=5)
        }))
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = recharge_energy_for(game_state, Pid.P1, amount=2)
        game_state = step_skill(
            game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST, cost=ActualDice({Element.PYRO: 3}),
        )
        assert_last_dmg(self, game_state, Pid.P1, last_index=2, amount=2, elem=Element.PIERCING)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, amount=2, elem=Element.PIERCING)
        assert_last_dmg(
            self, game_state, Pid.P1, last_index=0, amount=3, elem=Element.PHYSICAL,
            target=StaticTarget.from_char_id(Pid.P2, 1), num=3,
        )
        self.assertEqual(game_state.player1.hand_cards.num_cards(), 0)
        self.assertIn(FestiveFiresStatus, game_state.player1.combat_statuses)
        self.assertEqual(game_state.player1.combat_statuses.just_find(FestiveFiresStatus).usages, 2)

    def test_shield_of_passion_status(self):
        base_state = self.BASE_GAME
        base_state = add_combat_status(base_state, Pid.P1, ShieldOfPassionStatus)
        self.assertEqual(base_state.player1.combat_statuses.just_find(ShieldOfPassionStatus).usages, 2)
        base_state = add_dmg_listener(base_state, Pid.P1)

        # check dmg to non active player does not get reduced
        game_state = base_state
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, Pid.P1, char_id=3)
        assert_last_dmg(self, game_state, Pid.P1, amount=2)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ShieldOfPassionStatus).usages, 2)

        game_state = base_state
        game_state = simulate_status_dmg(game_state, 1, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=0)
        self.assertEqual(game_state.player1.combat_statuses.just_find(ShieldOfPassionStatus).usages, 1)

        game_state = base_state
        game_state = simulate_status_dmg(game_state, 2, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=0)
        self.assertNotIn(ShieldOfPassionStatus, game_state.player1.combat_statuses)

        game_state = base_state
        game_state = simulate_status_dmg(game_state, 3, Element.PHYSICAL, Pid.P1)
        assert_last_dmg(self, game_state, Pid.P1, amount=1)
        self.assertNotIn(ShieldOfPassionStatus, game_state.player1.combat_statuses)

    def test_festive_fires_status(self):
        game_state = self.BASE_GAME
        game_state = replace_deck_cards(game_state, Pid.P1, OrderedCards.from_empty())
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Paimon: 2}))
        game_state = add_dmg_listener(game_state, Pid.P1)
        game_state = add_combat_status(game_state, Pid.P1, FestiveFiresStatus)
        self.assertEqual(game_state.player1.combat_statuses.just_find(FestiveFiresStatus).usages, 2)

        # check not triggered when hand cards > 2
        game_state = next_round(game_state)
        self.assertEqual(len(get_dmg_listener_data(game_state, Pid.P1)), 0)
        self.assertEqual(game_state.player1.combat_statuses.just_find(FestiveFiresStatus).usages, 2)

        # check triggered when hand cards == 1
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({Paimon: 1}))
        game_state = next_round(game_state)
        game_state = assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.PYRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2), num=1, clear=True,
        )
        self.assertEqual(game_state.player1.combat_statuses.just_find(FestiveFiresStatus).usages, 1)

        # check triggered when hand cards == 0
        game_state = replace_hand_cards(game_state, Pid.P1, Cards.from_empty())
        game_state = next_round(game_state)
        assert_last_dmg(
            self, game_state, Pid.P1, amount=1, elem=Element.PYRO,
            target=StaticTarget.from_player_active(game_state, Pid.P2), num=1,
        )
        self.assertNotIn(FestiveFiresStatus, game_state.player1.combat_statuses)

    def test_talent_card(self):
        base_state = self.BASE_GAME
        base_state = replace_deck_cards(base_state, Pid.P1, OrderedCards.from_empty())
        base_state = add_dmg_listener(base_state, Pid.P1)
        base_state = grant_all_infinite_revival(base_state)
        
        """ check only triggered when hands <= 1, once per round """
        game_state = base_state
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({RockinInAFlamingWorld: 1, Paimon: 2}))
        game_state = end_round(game_state, Pid.P2)
        game_state = play_dice_only_card(
            game_state, Pid.P1, RockinInAFlamingWorld, cost=ActualDice({Element.PYRO: 3})
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=2, normal_attack=True)

        equipped_state = game_state
        equipped_state = replace_hand_cards(equipped_state, Pid.P1, Cards({Paimon: 1}))

        # normal attack
        game_state = equipped_state
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=4, normal_attack=True, elem=Element.PHYSICAL)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, normal_attack=True, elem=Element.PHYSICAL)
        game_state = end_round(next_round_with_great_omni(game_state), Pid.P2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=4, normal_attack=True, elem=Element.PHYSICAL)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, normal_attack=True, elem=Element.PHYSICAL)

        # elemental skill
        game_state = equipped_state
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=4, elemental_skill=True, elem=Element.PYRO)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL2)
        assert_last_dmg(self, game_state, Pid.P1, amount=2, elemental_skill=True, elem=Element.PYRO)

        # elemental burst
        game_state = equipped_state
        game_state = recharge_energy_for(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.ELEMENTAL_BURST)
        assert_last_dmg(self, game_state, Pid.P1, last_index=2, amount=2, elem=Element.PIERCING)
        assert_last_dmg(self, game_state, Pid.P1, last_index=1, amount=2, elem=Element.PIERCING)
        assert_last_dmg(self, game_state, Pid.P1, last_index=0, amount=5, elem=Element.PHYSICAL)

        """ check dmg boost on equip """
        game_state = base_state
        game_state = replace_hand_cards(game_state, Pid.P1, Cards({RockinInAFlamingWorld: 1, Paimon: 1}))
        game_state = play_dice_only_card(
            game_state, Pid.P1, RockinInAFlamingWorld, cost=ActualDice({Element.PYRO: 3})
        )
        assert_last_dmg(self, game_state, Pid.P1, amount=4, normal_attack=True, elem=Element.PHYSICAL)
