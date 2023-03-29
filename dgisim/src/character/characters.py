from __future__ import annotations
from typing import Optional

from dgisim.src.character.character import Character
from dgisim.src.event.event_pre import EventPre
from dgisim.src.helper.level_print import level_print, INDENT, level_print_single


class Characters:
    def __init__(self, characters: tuple[Character, ...], active_character_id: Optional[int]):
        self._characters = characters
        self._active_character_id = active_character_id

    @classmethod
    def from_default(cls, characters: tuple[Character, ...]) -> Characters:
        return cls(characters, None)

    def get_characters(self) -> tuple[Character, ...]:
        return self._characters

    def get_active_character_id(self) -> Optional[int]:
        return self._active_character_id

    def get_active_character(self) -> Optional[Character]:
        if self._active_character_id is None:
            return None
        return self._characters[self._active_character_id]

    def get_active_character_name(self) -> str:
        char = self.get_active_character()
        if char is None:
            return "None"
        return char.name()

    def get_id(self, character: Character) -> Optional[int]:
        for c in self._characters:
            if character is c:
                return c.get_id()
        return None

    def get_skills(self) -> tuple[EventPre, ...]:
        active_character = self.get_active_character()
        if active_character is None:
            return tuple()
        # TODO
        # return active_character.skills()
        return tuple()

    def char_id_valid(self, char_id: int) -> bool:
        return char_id >= 0 and char_id < len(self._characters)

    def get_swappable_ids(self) -> tuple[int, ...]:
        return tuple([
            i
            for i, c in enumerate(self._characters)
            if not c.defeated()
        ])

    def num_characters(self) -> int:
        return len(self._characters)

    def factory(self) -> CharactersFactory:
        return CharactersFactory(self)

    def _all_unique_data(self) -> tuple:
        return (self._characters, self._active_character_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Characters):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        return self.to_string(0)

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        new_new_indent = new_indent + INDENT
        return level_print({
            "Active Character": self.get_active_character_name(),
            "Characters": level_print(dict([
                (char.name(), char.to_string(new_new_indent))
                for char in self._characters
            ]), new_indent),
        }, indent)


class CharactersFactory:

    def __init__(self, characters: Characters):
        self._characters = characters.get_characters()
        self._active_character_id = characters.get_active_character_id()

    def character(self, char: Character) -> CharactersFactory:
        chars = list(self._characters)
        for i, c in enumerate(chars):
            if c.get_id() == char.get_id():
                chars[i] = char
                break
        self._characters = tuple(chars)
        return self

    def characters(self, chars: tuple[Character]) -> CharactersFactory:
        self._characters = chars
        return self

    def active_character_id(self, id: int) -> CharactersFactory:
        self._active_character_id = id
        return self

    def build(self) -> Characters:
        return Characters(
            self._characters,
            self._active_character_id,
        )
