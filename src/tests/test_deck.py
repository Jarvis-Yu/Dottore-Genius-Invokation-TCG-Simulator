import unittest

from src.dgisim.card.card import *
from src.dgisim.character.character import *
from src.dgisim.deck import Deck, FrozenDeck, MutableDeck
from src.dgisim.encoding.encoding_plan import encoding_plan
from src.dgisim.helper.hashable_dict import HashableDict
from src.dgisim.mode import DefaultMode
from src.dgisim.state.game_state import GameState


class TestDeck(unittest.TestCase):
    def test_valid_decks(self):
        deck1 = FrozenDeck(
            chars=(
                Keqing,
                Kaeya,
                AratakiItto,
            ),
            cards=HashableDict({
                ThunderingPenance: 2,
                ColdBloodedStrike: 2,
                AratakiIchiban: 2,
                RavenBow: 2,
                MagicGuide: 1,
                WhiteIronGreatsword: 1,
                WhiteTassel: 2,
                TravelersHandySword: 2,
                Xudong: 2,
                KnightsOfFavoniusLibrary: 2,
                IHaventLostYet: 2,
                JueyunGuoba: 2,
                LotusFlowerCrisp: 2,
                TeyvatFriedEgg: 2,
                Starsigns: 2,
                LeaveItToMe: 2,
            })
        )
        assert len(deck1.chars) == 3
        assert sum(deck1.cards.values()) == 30
        self.assertTrue(DefaultMode().valid_deck(deck1))
        self.assertTrue(DefaultMode().partially_valid_deck(deck1))
        game_state = GameState.from_decks(DefaultMode(), deck1, deck1)

    def test_invalid_for_not_enough_char(self):
        deck1 = FrozenDeck(
            chars=(
                Keqing,
                Kaeya,
            ),
            cards=HashableDict({
                ThunderingPenance: 2,
                ColdBloodedStrike: 2,
                MondstadtHashBrown: 2,
                RavenBow: 2,
                MagicGuide: 1,
                WhiteIronGreatsword: 1,
                WhiteTassel: 2,
                TravelersHandySword: 2,
                Xudong: 2,
                KnightsOfFavoniusLibrary: 2,
                IHaventLostYet: 2,
                JueyunGuoba: 2,
                LotusFlowerCrisp: 2,
                TeyvatFriedEgg: 2,
                Starsigns: 2,
                LeaveItToMe: 2,
            })
        )
        assert len(deck1.chars) < 3
        assert sum(deck1.cards.values()) == 30
        self.assertFalse(DefaultMode().valid_deck(deck1))
        self.assertTrue(DefaultMode().partially_valid_deck(deck1))

    def test_invalid_for_unmatching_talent_card(self):
        deck1 = FrozenDeck(
            chars=(
                Keqing,
                Kaeya,
                Tighnari,
            ),
            cards=HashableDict({
                ThunderingPenance: 2,
                ColdBloodedStrike: 2,
                StreamingSurge: 2,  # faulty card
                RavenBow: 2,
                MagicGuide: 1,
                WhiteIronGreatsword: 1,
                WhiteTassel: 2,
                TravelersHandySword: 2,
                Xudong: 2,
                KnightsOfFavoniusLibrary: 2,
                IHaventLostYet: 2,
                JueyunGuoba: 2,
                LotusFlowerCrisp: 2,
                TeyvatFriedEgg: 2,
                Starsigns: 2,
                LeaveItToMe: 2,
            })
        )
        assert len(deck1.chars) == 3
        assert sum(deck1.cards.values()) == 30
        self.assertFalse(DefaultMode().valid_deck(deck1))
        self.assertFalse(DefaultMode().partially_valid_deck(deck1))

    def test_mutability(self):
        immutable_deck = FrozenDeck(
            chars=(
                Klee,
                KaedeharaKazuha,
            ),
            cards=HashableDict({
                PoundingSurprise: 1,
                GamblersEarrings: 2,
            })
        )
        mutable_deck = immutable_deck.to_mutable()
        assert not mutable_deck.immutable
        immutable_again_deck = mutable_deck.to_frozen()
        self.assertEqual(immutable_deck, immutable_again_deck)
        self.assertEqual(mutable_deck, immutable_again_deck.to_mutable())

    def test_cards(self):
        def test_card(card: type[Card], chars: list[type[Character]]) -> bool:
            return card.valid_in_deck(MutableDeck(chars, {}))

        self.assertFalse(test_card(LightningStiletto, [Keqing]))

    def test_json_sl(self):
        immutable_deck = FrozenDeck(
            chars=(
                Klee,
                KaedeharaKazuha,
            ),
            cards=HashableDict({
                PoundingSurprise: 1,
                GamblersEarrings: 2,
            })
        )
        json_str = immutable_deck.to_json()
        deck_read = MutableDeck.from_json(json_str)
        self.assertEqual(immutable_deck, deck_read)

    def test_encoding_decoding(self):
        deck: Deck = MutableDeck(
            chars=[
                Klee,
                KaedeharaKazuha,
                Keqing,
            ],
            cards={
                PoundingSurprise: 1,
                GamblersEarrings: 2,
            }
        )
        encoding = deck.encoding(encoding_plan)
        deck_read: Deck | None = MutableDeck.decoding(encoding, encoding_plan)
        self.assertEqual(deck, deck_read)

        deck = FrozenDeck(
            chars=(
                Klee,
                KaedeharaKazuha,
            ),
            cards=HashableDict({
                PoundingSurprise: 1,
                GamblersEarrings: 2,
            })
        )
        encoding = deck.encoding(encoding_plan)
        deck_read = FrozenDeck.decoding(encoding, encoding_plan)
        self.assertEqual(deck, deck_read)
