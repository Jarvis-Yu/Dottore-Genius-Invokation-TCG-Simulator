import copy
import itertools
from enum import Enum
from typing import cast, no_type_check, TYPE_CHECKING, Union

from typing_extensions import Self

from ..state.enums import Pid
from .mappings import *

if TYPE_CHECKING:
    from ..card.card import Card
    from ..character.character import Character
    from ..effect.effect import Effect
    from ..mode import Mode
    from ..state.game_state import GameState
    from ..status.status import Status
    from ..summon.summon import Summon
    from ..support.support import Support

__all__ = [
    "EncodingPlan",
    "LazyEncodingPlan",
    "encoding_plan",
    "GameItem",
    "GameItemType",
]


GameItem = Union["Card", "Character", "Effect", "Mode", "Status", "Summon", "Support"]
GameItemType = type["Card"] | type["Character"] | type["Effect"] | type["Mode"] | type["Status"] | type["Summon"] | type["Support"]


class EncodingPlan:
    _flip_cache: None | Self = None

    """
    This is the class for GameState encoding planning.
    It contains information on the codes for each type of item.
    """
    def __init__(
            self,
            mode_mapping: dict[type["Mode"], int],
            card_mapping: dict[type["Card"], int],
            enum_mapping: dict[Enum, int],
            char_mapping: dict[type["Character"], int],
            effect_mapping: dict[type["Effect"], int],
            status_mapping: dict[type["Status"], int],
            summon_mapping: dict[type["Summon"], int],
            support_mapping: dict[type["Support"], int],
            phase_base: int = 450,
            cards_fixed_len: int = 50,
            dice_fixed_len: int = 20,
            status_fixed_len: int = 7,
            statuses_fixed_len: int = 10,
            char_hidden_fixed_len: int = 4,
            char_stt_fixed_len: int = 13,
            player_hidden_fixed_len: int = 10,
            player_combat_fixed_len: int = 10,
            summons_fixed_len: int = 4,
            supports_fixed_len: int = 4,
            effect_fixed_len: int = 25,
            effects_fixed_len: int = 40,
            perspective: Pid = Pid.P1,
    ) -> None:
        """
        :param mode_mapping: a mapping from mode to code.
        :param card_mapping: a mapping from card to code.
        :param char_mapping: a mapping from character to code.
        :param effect_mapping: a mapping from effect to code.
        :param status_mapping: a mapping from status to code.
        :param summon_mapping: a mapping from summon to code.
        :param support_mapping: a mapping from support to code.
        :param cards_fixed_len: the fixed length of any encoded cards vector.
        :param status_fixed_len: the default fixed length of encoded status vector.
        :param statuses_fixed_len: the default fixed length of encoded statuses vector.
        :param char_hidden_fixed_len: the default fixed length of encoded character hidden statuses vector.
        :param char_stt_fixed_len: the default fixed length of encoded character statuses vector.
        :param player_hidden_fixed_len: the default fixed length of encoded player hidden statuses vector.
        :param player_combat_fixed_len: the default fixed length of encoded player combat statuses vector.
        :param summons_fixed_len: the default fixed length of encoded summons vector.
        :param supports_fixed_len: the default fixed length of encoded supports vector.
        :param effect_fixed_len: the default fixed length of encoded effect vector.
        :param effects_fixed_len: the default fixed length of encoded effects vector.
        """
        self._enum_mapping = enum_mapping
        self._card_mapping = card_mapping
        self._char_mapping = char_mapping
        self._effect_mapping = effect_mapping
        self._mode_mapping = mode_mapping
        self._status_mapping = status_mapping
        self._summon_mapping = summon_mapping
        self._support_mapping = support_mapping
        self._perspective = perspective
        self.PHASE_BASE = phase_base
        self.CARDS_FIXED_LEN = cards_fixed_len
        self.DICE_FIXED_LEN = dice_fixed_len
        self.STATUS_FIXED_LEN = status_fixed_len
        self.STATUSES_FIXED_LEN = statuses_fixed_len
        self.CHAR_HIDDEN_FIXED_LEN = char_hidden_fixed_len
        self.CHAR_STT_FIXED_LEN = char_stt_fixed_len
        self.PLAYER_HIDDEN_FIXED_LEN = player_hidden_fixed_len
        self.PLAYER_COMBAT_FIXED_LEN = player_combat_fixed_len
        self.SUMMONS_FIXED_LEN = summons_fixed_len
        self.SUPPORTS_FIXED_LEN = supports_fixed_len
        self.EFFECT_FIXED_LEN = effect_fixed_len
        self.EFFECTS_FIXED_LEN = effects_fixed_len

        from ..element import Element
        self.ACTION_LOCAL_SIZE = 5 + self.CARDS_FIXED_LEN
        self.ACTION_FULL_SIZE = (
            self.ACTION_LOCAL_SIZE  # size of cards
            + self.DICE_FIXED_LEN  # dice of instruction
            + 3  # StaticTarget of instruction
            + 3  # StaticTarget of instruction
        )
        self.INSTRUCTION_SIZE = self.ACTION_FULL_SIZE - self.ACTION_LOCAL_SIZE
        from ..card.card import Card
        from ..character.character import Character
        from ..effect.effect import Effect
        from ..mode import Mode
        from ..status.status import Status
        from ..summon.summon import Summon
        from ..support.support import Support
        self._TYPED_MAPPING = {
            Enum: self._enum_mapping,
            Card: self._card_mapping,
            Character: self._char_mapping,
            Effect: self._effect_mapping,
            Mode: self._mode_mapping,
            Status: self._status_mapping,
            Summon: self._summon_mapping,
            Support: self._support_mapping,
        }
        self._id_item_mapping: dict[int, GameItemType] = {}
        for d in self._TYPED_MAPPING.values():
            assert isinstance(d, dict)
            for item, code in d.items():
                self._id_item_mapping[code] = item  # type: ignore

    def is_valid(self) -> bool:
        """
        :returns: True if all codes are unique and non-zero.
        """
        all_vals = list(itertools.chain(
            self._enum_mapping.values(),
            self._card_mapping.values(),
            self._char_mapping.values(),
            self._mode_mapping.values(),
            self._status_mapping.values(),
            self._summon_mapping.values(),
            self._support_mapping.values(),
        ))
        all_vals_set = set(all_vals)
        return len(all_vals) == len(all_vals_set) and 0 not in all_vals_set

    @no_type_check
    def encode_item(
            self,
            item: GameItem | GameItemType | Enum,
    ) -> int:
        """
        :returns: the code for the given item.
        """
        from ..card.card import Card
        from ..character.character import Character
        from ..effect.effect import Effect
        from ..mode import Mode
        from ..status.status import Status
        from ..summon.summon import Summon
        from ..support.support import Support
        _og_item = item
        if isinstance(item, Enum):
            item_category = Enum
            if self._perspective is Pid.P2 and isinstance(item, Pid):
                item = item.other
        else:
            if isinstance(item, Card):
                item = type(item)
            elif isinstance(item, Summon):
                item = type(item)
            elif isinstance(item, Support):
                item = type(item)
            elif isinstance(item, Status):
                item = type(item)
            elif isinstance(item, Effect):
                item = type(item)
            elif isinstance(item, Character):
                item = type(item)
            elif isinstance(item, Mode):
                item = type(item)
            assert issubclass(item, Card | Character | Effect | Mode | Status | Summon | Support)
            if issubclass(item, Card):
                item_category = Card
            elif issubclass(item, Summon):
                item_category = Summon
            elif issubclass(item, Support):
                item_category = Support
            elif issubclass(item, Status):
                item_category = Status
            elif issubclass(item, Effect):
                item_category = Effect
            elif issubclass(item, Character):
                item_category = Character
            else:
                assert issubclass(item, Mode), f"Unknown item type: {item}"
                item_category = Mode
        mapping = cast(
            dict[GameItemType, int],
            self._TYPED_MAPPING[item_category],
        )
        if item not in mapping:
            # return -1
            raise Exception(
                f"Item has no code for {item} under category {item_category}; item was {_og_item}."
            )
        else:
            return mapping[item]

    def type_for(self, code: int) -> None | GameItemType:
        """
        :returns: the type of the item with the given code.
        """
        return self._id_item_mapping.get(code, None)

    def compatible_with(self, mode: "Mode") -> bool:
        """
        :returns: True if this encoding plan is compatible with the given mode.

        Note: currently only cards and characters are checked,
        all statuses are not.
        """
        return (
            mode.all_cards().issubset(self._card_mapping.keys())
            and mode.all_chars().issubset(self._char_mapping.keys())
        )

    def encode(self, game_state: "GameState", perspective: Pid) -> list[int]:
        return game_state.encoding(self, perspective)

    @property
    def game_encoding_size(self) -> int:
        """
        :returns: the size of the vector of any encoded game state.
        """
        from ..state.game_state import GameState
        return len(GameState.from_default().encoding(self))

    @property
    def action_encoding_size(self) -> int:
        """
        :returns: the size of the vector of any encoded action.
        """
        return self.ACTION_FULL_SIZE

    def perspective_version(self, pid: Pid) -> Self:
        if self._perspective is pid:
            return self
        if self._flip_cache is None:
            new_self = copy.copy(self)
            new_self._perspective = pid
            self._flip_cache = new_self
        return self._flip_cache

class LazyEncodingPlan(EncodingPlan):
    """
    A lazy version of EncodingPlan that does not encode anything, returning None.

    It can accelerate env.step() if you don't need the encoding instantly.
    """
    def encode(self, game_state: "GameState", perspective:Pid):
        """
        :returns: [].
        """
        return []

encoding_plan = EncodingPlan(
    enum_mapping=ENUM_MAPPING,
    card_mapping=CARD_MAPPING,
    char_mapping=CHAR_MAPPING,
    effect_mapping=EFFECT_MAPPING,
    mode_mapping=MODE_MAPPING,
    status_mapping=STT_MAPPING,
    summon_mapping=SUMM_MAPPING,
    support_mapping=SUPP_MAPPING,
)

if __name__ == "__main__":
    # sizing report
    from ..state.game_state import GameState
    from ..helper.level_print import level_print_single

    indent = 0
    game_state = GameState.from_default()
    encoding = encoding_plan.encode(game_state, Pid.P1)
    print(f"game_state size = {len(encoding)}")

    player = game_state.player1
    encoding = player.encoding(encoding_plan)
    print(f"player_state size = {len(encoding)}")

    deck = player.initial_deck
    encoding = deck.encoding(encoding_plan)
    print(f"deck size = {len(encoding)}")

    chars = player.characters
    encoding = chars.encoding(encoding_plan)
    print(f"chars size = {len(encoding)}")
