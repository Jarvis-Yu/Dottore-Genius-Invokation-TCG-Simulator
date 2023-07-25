from __future__ import annotations
from typing import Callable, Iterator, Optional, TYPE_CHECKING, Union, Iterable

if TYPE_CHECKING:
    from .character import Character
    from ..element import Element

__all__ = [
    "Characters",
]


class Characters:
    def __init__(self, characters: tuple[Character, ...], active_character_id: None | int):
        self._characters = characters
        self._active_character_id = active_character_id

    @classmethod
    def from_default(cls, characters: tuple[Character, ...]) -> Characters:
        return cls(characters, None)

    @classmethod
    def from_list(cls, characters: Iterable[type[Character]]) -> Characters:
        return Characters(
            tuple(
                char.from_default(i + 1)
                for i, char in enumerate(characters)
            ),
            None,
        )

    def get_characters(self) -> tuple[Character, ...]:
        return self._characters

    def get_active_character_id(self) -> None | int:
        return self._active_character_id

    def just_get_active_character_id(self) -> int:
        val = self.get_active_character_id()
        assert val is not None
        return val

    def get_character_in_activity_order(self) -> tuple[Character, ...]:
        for i, character in enumerate(self._characters):
            if character.get_id() == self._active_character_id:
                return self._characters[i:] + self._characters[:i]
        return self._characters

    def get_none_active_characters(self) -> tuple[Character, ...]:
        return tuple(
            char
            for char in self._characters
            if char.get_id() != self.get_active_character_id()
        )

    def get_alive_characters(self) -> tuple[Character, ...]:
        return tuple(
            char
            for char in self._characters
            if char.alive()
        )

    def get_character(self, id: int) -> None | Character:
        for character in self._characters:
            if id == character.get_id():
                return character
        return None

    def just_get_character(self, id: int) -> Character:
        character = self.get_character(id)
        if character is None:
            raise Exception("Character not found")
        return character

    def find_first_character(self, char_type: type[Character]) -> None | Character:
        return next(
            (char for char in self if type(char) is char_type),
            None
        )

    def get_active_character(self) -> None | Character:
        if self._active_character_id is None:
            return None
        return self.get_character(self._active_character_id)

    def just_get_active_character(self) -> Character:
        assert self._active_character_id is not None
        character = self.get_character(self._active_character_id)
        assert character is not None
        return character

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

    def get_by_id(self, id: int) -> Optional[Character]:  # pragma: no cover
        return self.get_character(id)

    def all_defeated(self) -> bool:
        return all([c.defeated() for c in self._characters])

    def char_id_valid(self, char_id: int) -> bool:
        return char_id >= 1 and char_id <= len(self._characters)

    def num_characters(self) -> int:
        return len(self._characters)

    def all_elems(self) -> set[Element]:
        return set(
            char.element()
            for char in self._characters
        )

    def factory(self) -> CharactersFactory:
        return CharactersFactory(self)

    def _all_unique_data(self) -> tuple:
        return (self._characters, self._active_character_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Characters):
            return False
        return self is other or self._all_unique_data() == other._all_unique_data()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __iter__(self) -> Iterator[Character]:
        return iter(self.get_characters())

    def contains(self, char: Character | type[Character]) -> bool:
        from .character import Character
        if isinstance(char, Character):
            return any(
                c == char
                for c in self._characters
            )
        else:  # assert char: type[Character]
            return any(
                type(c) is char
                for c in self._characters
            )

    def __contains__(self, char: Character | type[Character]) -> bool:
        return self.contains(char)

    def dict_str(self) -> Union[dict, str]:
        return {
            "Active Character": f"{self.get_active_character_id()}-{self.get_active_character_name()}",
            "Characters": dict([
                (f"{char.get_id()}-{char.name()}", char.dict_str())
                for char in self._characters
            ]),
        }


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

    def f_character(self, id: int, f: Callable[[Character], Character]) -> CharactersFactory:
        chars = list(self._characters)
        for i, c in enumerate(chars):
            if c.get_id() == id:
                chars[i] = f(c)
                break
        self._characters = tuple(chars)
        return self

    def f_active_character(self, f: Callable[[Character], Character]) -> CharactersFactory:
        assert self._active_character_id is not None
        return self.f_character(self._active_character_id, f)

    def characters(self, chars: tuple[Character, ...]) -> CharactersFactory:
        self._characters = chars
        return self

    def f_characters(self, f: Callable[[tuple[Character, ...]], tuple[Character, ...]]) -> CharactersFactory:
        self._characters = f(self._characters)
        return self

    def active_character_id(self, id: int) -> CharactersFactory:
        self._active_character_id = id
        return self

    def build(self) -> Characters:
        return Characters(
            self._characters,
            self._active_character_id,
        )
