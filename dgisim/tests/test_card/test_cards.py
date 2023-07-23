import unittest
from typing import cast

from dgisim.src.card.cards import Cards
from dgisim.src.card.card import Card, OmniCard

class CardA(Card):
    pass

class CardB(Card):
    pass

class CardC(Card):
    pass

class TestCards(unittest.TestCase):
    def test_is_legal(self):
        cards = Cards({CardA: 1, CardB: 0})
        self.assertTrue(cards.is_legal())

        cards = Cards({CardA: -1, CardB: 0})
        self.assertFalse(cards.is_legal())

    def test_empty(self):
        cards = Cards({CardA: 1, CardB: 0})
        self.assertFalse(cards.empty())

        cards = Cards({CardA: 0, CardB: 0})
        self.assertTrue(cards.empty())

    def test_cards(self):
        cards = Cards({CardA: 1})
        self.assertRaises(Exception, lambda: cards.remove(CardB))

        cards = cards + cast(dict[type[Card], int], {OmniCard: 1})
        tmp_cards = cards.remove(CardB)
        self.assertTrue(tmp_cards.is_legal())

    def test_remove_all(self):
        cards = Cards({CardA: 2, CardB: 19})
        tmp_cards = cards.remove_all(CardB)
        self.assertNotIn(CardB, tmp_cards)
        tmp_cards = cards.remove_all(CardC)
        self.assertIs(cards, tmp_cards)

    def test_eq_and_hash(self):
        cards1 = Cards({CardA: 114, CardC: 514})
        cards2 = Cards({CardC: 514, CardA: 114, CardB: 0})
        cards3 = Cards({CardB: 514, CardA: 114})
        cards4 = Cards({CardA: 1919, CardC: 810})
        self.assertEqual(cards1, cards2)
        self.assertEqual(hash(cards1), hash(cards2))
        self.assertNotEqual(cards3, cards2)
        self.assertNotEqual(hash(cards3), hash(cards2))
        self.assertNotEqual(cards4, cards2)
        self.assertNotEqual(hash(cards4), hash(cards2))
        self.assertNotEqual(cards1, "cards1")

    def test_to_dict(self):
        cards = Cards({CardB: 1, CardC: 5})
        d = cards.to_dict()
        self.assertEqual(d[CardB], 1)
        self.assertEqual(d[CardC], 5)
        self.assertEqual(len(d), 2)
