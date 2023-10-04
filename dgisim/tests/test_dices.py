import unittest

from dgisim.src.dice import *
from dgisim.src.element import *
from dgisim.src.helper import just


class TestDice(unittest.TestCase):
    def test_pick_random_dice(self):
        dice = Dice(ActualDice.from_random(8).to_dict())
        left, picked = dice.pick_random_dice(3)
        self.assertEqual(picked.num_dice(), 3)
        self.assertEqual(left.num_dice(), 5)
        sum_backed = left + picked
        self.assertEqual(dice, sum_backed)
        self.assertEqual(hash(dice), hash(sum_backed))

        left, picked = dice.pick_random_dice(0)
        self.assertIs(dice, left)
        self.assertEqual(picked.num_dice(), 0)

    def test_contains(self):
        dice = Dice({Element.ANEMO: 3, Element.PYRO: 0, Element.OMNI: -2})
        self.assertIn(Element.ANEMO, dice)
        self.assertNotIn(Element.PYRO, dice)
        self.assertNotIn(Element.OMNI, dice)

    def test_eq(self):
        dice = Dice({})
        self.assertNotEqual(dice, "dice")

    def test_to_dict(self):
        random_actual_dice = ActualDice.from_random(8)
        _dice = random_actual_dice._dice
        to_dict = random_actual_dice.to_dict()
        dice1 = Dice(_dice)
        dice2 = Dice(to_dict)
        self.assertEqual(dice1, dice2)
        self.assertIsNot(_dice, to_dict)

    def test_from_dice(self):
        dice = Dice({Element.PYRO: 6, Element.OMNI: 2})
        actual_dice = ActualDice.from_dice(dice)
        assert actual_dice is not None
        self.assertEqual(dice._dice, actual_dice._dice)

        dice = Dice({Element.PYRO: 6, Element.ANY: 2})
        actual_dice = ActualDice.from_dice(dice)
        self.assertIsNone(actual_dice)

        dice = Dice({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: 2})
        abstract_dice = AbstractDice.from_dice(dice)
        assert abstract_dice is not None
        self.assertEqual(dice._dice, abstract_dice._dice)

        dice = Dice({Element.PYRO: 6, Element.OMNI: 2, Element.ANY: -2})
        abstract_dice = AbstractDice.from_dice(dice)
        self.assertIsNone(abstract_dice)

    def test_just_satisfy_pure_request(self):
        requirement = AbstractDice({
            Element.PYRO: 2,
        })
        payment1 = ActualDice({
            Element.OMNI: 2,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.PYRO: 1,
        })
        payment3 = ActualDice({
            Element.PYRO: 2,
        })
        payment4 = ActualDice({
            Element.PYRO: 3,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))

    def test_just_satisfy_typical_1pure_2any(self):
        requirement = AbstractDice({
            Element.DENDRO: 1,
            Element.ANY: 2,
        })
        payment1 = ActualDice({
            Element.OMNI: 3,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.PYRO: 1,
            Element.ELECTRO: 1,
        })
        payment3 = ActualDice({
            Element.DENDRO: 3,
        })
        payment4 = ActualDice({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertTrue(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_elemental_skill(self):
        requirement = AbstractDice({
            Element.ELECTRO: 3,
        })
        payment1 = ActualDice({
            Element.OMNI: 3,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.ELECTRO: 2,
        })
        payment3 = ActualDice({
            Element.ELECTRO: 3,
        })
        payment4 = ActualDice({
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.ANEMO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 1,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_just_satisfy_typical_all_omni(self):
        requirement = AbstractDice({
            Element.OMNI: 4,
        })
        payment1 = ActualDice({
            Element.OMNI: 4,
        })
        payment2 = ActualDice({
            Element.OMNI: 1,
            Element.ELECTRO: 3,
        })
        payment3 = ActualDice({
            Element.ELECTRO: 4,
        })
        payment4 = ActualDice({
            Element.OMNI: 4,
            Element.DENDRO: 1,
        })
        payment5 = ActualDice({
            Element.GEO: 2,
            Element.ANEMO: 2,
        })
        self.assertTrue(payment1.just_satisfy(requirement))
        self.assertTrue(payment2.just_satisfy(requirement))
        self.assertTrue(payment3.just_satisfy(requirement))
        self.assertFalse(payment4.just_satisfy(requirement))
        self.assertFalse(payment5.just_satisfy(requirement))

    def test_basically_satisfy_successes(self):
        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.CRYO: 3, Element.ANEMO: 1})
        self.assertEqual(payment.basically_satisfy(requirement), ActualDice({Element.CRYO: 3}))

        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.CRYO: 2, Element.OMNI: 2})
        self.assertEqual(payment.basically_satisfy(requirement),
                         ActualDice({Element.CRYO: 2, Element.OMNI: 1}))

        requirement = AbstractDice({Element.OMNI: 3})
        payment = ActualDice({Element.ANEMO: 1, Element.ELECTRO: 1,
                              Element.PYRO: 1, Element.OMNI: 2})
        self.assertEqual(just(payment.basically_satisfy(requirement))[Element.OMNI], 2)

    def test_basically_satisfy_failures(self):
        requirement = AbstractDice({Element.ANY: 8})
        payment = ActualDice({Element.OMNI: 7})
        self.assertIsNone(payment.basically_satisfy(requirement))

        requirement = AbstractDice({Element.OMNI: 4})
        payment = ActualDice({Element.GEO: 3, Element.ELECTRO: 2,
                              Element.HYDRO: 1, Element.DENDRO: 3})
        self.assertIsNone(payment.basically_satisfy(requirement))

    def test_ordered_actual_dice(self):
        dice = ActualDice({
            Element.HYDRO: 1,
            Element.ELECTRO: 1,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 1,
            Element.OMNI: 1,
            Element.DENDRO: 1,
            Element.PYRO: 1,
        })
        self.assertEqual(
            tuple(dice.readonly_dice_ordered(None).keys()),
            ActualDice._LEGAL_ELEMS_ORDERED,
        )

    def test_ordered_actual_dice_with_diff_nums(self):
        dice = ActualDice({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        keys = tuple(dice.readonly_dice_ordered(None).keys())
        expected_order = (
            Element.OMNI,
            Element.CRYO,
            Element.ELECTRO,
            Element.DENDRO,
            Element.HYDRO,
            Element.PYRO,
            Element.GEO,
            Element.ANEMO,
        )
        self.assertEqual(
            keys,
            expected_order,
        )

    def test_ordered_actual_dice_with_characters(self):
        dice = ActualDice({
            Element.HYDRO: 1,
            Element.ELECTRO: 2,
            Element.ANEMO: 1,
            Element.GEO: 1,
            Element.CRYO: 2,
            Element.OMNI: 1,
            Element.DENDRO: 2,
            Element.PYRO: 1,
        })
        from dgisim.src.card.cards import Cards
        from dgisim.src.character.character import AratakiItto, Klee, Keqing
        from dgisim.src.character.characters import Characters
        from dgisim.src.mode import DefaultMode
        from dgisim.src.state.player_state import PlayerState
        player_state = PlayerState.from_chars_cards(
            DefaultMode(),
            Characters.from_iterable(
                [AratakiItto, Klee, Keqing]
            ).factory().active_character_id(2).build(),
            Cards({}),
        )
        keys = tuple(dice.readonly_dice_ordered(player_state).keys())
        expected_order = (
            Element.OMNI,
            Element.ELECTRO,
            Element.PYRO,
            Element.GEO,
            Element.CRYO,
            Element.DENDRO,
            Element.HYDRO,
            Element.ANEMO,
        )
        self.assertEqual(
            keys,
            expected_order,
        )
