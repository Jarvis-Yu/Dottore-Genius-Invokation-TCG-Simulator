import unittest

from dgisim.src.character.characters import Characters
from dgisim.src.character.character import *
from dgisim.src.state.game_state import GameState
from dgisim.tests.helpers.game_state_templates import ACTION_TEMPLATE


class TestCharacters(unittest.TestCase):
    def test_from_list(self):
        chars = Characters.from_iterable([
            RhodeiaOfLoch,
            Keqing,
            Tighnari,
        ])
        self.assertIsInstance(chars.get_character(1), RhodeiaOfLoch)
        self.assertIsInstance(chars.get_character(2), Keqing)
        self.assertIsInstance(chars.get_character(3), Tighnari)

        chars = Characters.from_iterable([
            Kaeya,
            Tighnari,
            Kaeya,
        ])
        self.assertIsInstance(chars.get_character(1), Kaeya)
        self.assertIsInstance(chars.get_character(2), Tighnari)
        self.assertIsInstance(chars.get_character(3), Kaeya)

    def test_get_character_in_activity_order(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(2).build()
            ).build()
        ).build()
        ordered_chars = base_game.get_player1().get_characters().get_character_in_activity_order()
        self.assertEqual(ordered_chars[0].get_id(), 2)
        self.assertEqual(ordered_chars[1].get_id(), 3)
        self.assertEqual(ordered_chars[2].get_id(), 1)

        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(1).build()
            ).build()
        ).build()
        ordered_chars = base_game.get_player1().get_characters().get_character_in_activity_order()
        self.assertEqual(ordered_chars[0].get_id(), 1)
        self.assertEqual(ordered_chars[1].get_id(), 2)
        self.assertEqual(ordered_chars[2].get_id(), 3)

        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(3).build()
            ).build()
        ).build()
        ordered_chars = base_game.get_player1().get_characters().get_character_in_activity_order()
        self.assertEqual(ordered_chars[0].get_id(), 3)
        self.assertEqual(ordered_chars[1].get_id(), 1)
        self.assertEqual(ordered_chars[2].get_id(), 2)

        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_characters(
                lambda cs: cs.factory().active_character_id(None).build()  # type: ignore
            ).build()
        ).build()
        characters = base_game.get_player1().get_characters()
        ordered_chars = characters.get_character_in_activity_order()
        self.assertEqual(ordered_chars, characters._characters)

    def test_get_none_active_characters(self):
        characters = Characters.from_iterable([Keqing, Keqing, Keqing])
        self.assertIsNone(characters.get_active_character_id())
        ordered_chars = characters.get_none_active_characters()
        self.assertEqual(len(ordered_chars), 3)

        characters = characters.factory().active_character_id(2).build()
        ordered_chars = characters.get_none_active_characters()
        self.assertEqual(ordered_chars[0].get_id(), 1)
        self.assertEqual(ordered_chars[1].get_id(), 3)

    def test_get_character(self):
        characters = Characters.from_iterable([Kaeya, RhodeiaOfLoch, Tighnari])
        self.assertIsInstance(characters.get_character(2), RhodeiaOfLoch)
        self.assertIsNone(characters.get_character(4))
        self.assertIsNone(characters.get_character(0))

    def test_just_get_character(self):
        characters = Characters.from_iterable([Kaeya, RhodeiaOfLoch, Tighnari])
        for i in range(1, 4):
            characters.just_get_character(i)
        self.assertRaises(Exception, lambda: characters.just_get_character(0))
        self.assertRaises(Exception, lambda: characters.just_get_character(4))

    def test_find_first_character(self):
        characters = Characters.from_iterable([Kaeya, Tighnari, Tighnari])
        char = characters.find_first_character(Tighnari)
        assert char is not None
        self.assertEqual(char.get_id(), 2)
        char = characters.find_first_character(Kaeya)
        assert char is not None
        self.assertEqual(char.get_id(), 1)
        char = characters.find_first_character(Keqing)
        self.assertIsNone(char)

    def test_get_active_character(self):
        chars = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        active_char = chars.get_active_character()
        self.assertIsNone(active_char)
        chars = chars.factory().active_character_id(3).build()
        active_char = chars.get_active_character()
        self.assertIsInstance(active_char, Keqing)

    def test_get_active_character_name(self):
        chars = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        name = chars.get_active_character_name()
        self.assertEqual(name, "None")
        chars = chars.factory().active_character_id(2).build()
        name = chars.get_active_character_name()
        self.assertEqual(name, "RhodeiaOfLoch")

    def test_num_characters(self):
        chars = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        self.assertEqual(chars.num_characters(), 3)
        chars = Characters.from_iterable(
            [RhodeiaOfLoch, RhodeiaOfLoch, Keqing, Tighnari, Tighnari, Kaeya]
        )
        self.assertEqual(chars.num_characters(), 6)

    def test_eq_and_hash(self):
        chars1 = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        chars2 = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        chars3 = Characters.from_iterable([Tighnari, RhodeiaOfLoch, Keqing])
        self.assertEqual(chars1, chars2)
        self.assertEqual(hash(chars1), hash(chars2))
        self.assertNotEqual(chars1, chars3)
        self.assertNotEqual(hash(chars1), hash(chars3))

        chars1 = chars1.factory().active_character_id(20).build()
        chars2 = chars2.factory().active_character_id(20).build()
        self.assertEqual(chars1, chars2)
        self.assertEqual(hash(chars1), hash(chars2))

        chars2 = chars2.factory().active_character_id(19).build()
        self.assertNotEqual(chars1, chars2)
        self.assertNotEqual(hash(chars1), hash(chars2))
        self.assertNotEqual(chars1, "chars1")

    def test_contains(self):
        chars = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        self.assertIn(Keqing.from_default(3), chars)
        self.assertIn(Keqing, chars)
        self.assertIn(RhodeiaOfLoch, chars)
        self.assertNotIn(RhodeiaOfLoch.from_default(1).factory().hp(2).build(), chars)
        self.assertNotIn(Tighnari, chars)

    def test_factory(self):
        chars = Characters.from_iterable([RhodeiaOfLoch, RhodeiaOfLoch, Keqing])
        chars = chars.factory().characters((Kaeya.from_default(2), Tighnari.from_default(3))).build()
        self.assertIn(Kaeya, chars)
        self.assertIn(Tighnari, chars)
        chars = chars.factory().f_characters(
            lambda cs: tuple(c.factory().hp(c.get_id()**2).build() for c in cs)
        ).build()
        self.assertEqual(chars.just_get_character(2).get_hp(), 4)
        self.assertEqual(chars.just_get_character(3).get_hp(), 9)
