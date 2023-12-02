from __future__ import annotations
from collections import Counter
from itertools import chain
from typing import Callable, Optional, Union, TYPE_CHECKING
from typing_extensions import Self

from ..character import character as chr
from ..status import statuses as sts
from ..support import support as sp

from ..card.cards import Cards
from ..character.characters import Characters
from ..dice import ActualDice
from ..helper.hashable_dict import HashableDict
from ..summon.summons import Summons
from ..support.supports import Supports

from .enums import Act

if TYPE_CHECKING:
    from ..deck import Deck
    from ..encoding.encoding_plan import EncodingPlan
    from ..mode import Mode

__all__ = [
    "PlayerState",
]


class PlayerState:
    """
    A class that holds all immutable data of a player.
    """

    def __init__(
        self,
        phase: Act,
        consec_action: bool,
        characters: Characters,
        hidden_statuses: sts.Statuses,
        combat_statuses: sts.Statuses,
        summons: Summons,
        supports: Supports,
        card_redraw_chances: int,
        dice_reroll_chances: int,
        dice: ActualDice,
        hand_cards: Cards,
        deck_cards: Cards,
        publicly_used_cards: Cards,
        publicly_gained_cards: Cards,
    ):
        """
        :param phase: the phase the player is in.
        :param consec_action: whether the player should act consecutively.
        :param characters: the characters.
        :param hidden_stateses: the hidden statuses.
        :param combet_statuses: the combat statuses.
        :param summons: the summons.
        :param supports: the supports.
        :param card_redraw_chances: the number of times a player can redraw cards.
        :param dice_reroll_chances: the number of time a player can reroll dice.
        :param dice: current dice in hand.
        :param hand_cards: current hand cards.
        :param deck_cards: cards in deck to be drawn.
        :param publicly_used_cards: cards the player has used that the opponent knows for sure.
        :param publicly_gained_cards: cards the player has gained that the opponent knows for sure.
        """
        # REMINDER: don't forget to update factory when adding new fields
        self._phase = phase
        self._consec_action = consec_action
        self._card_redraw_chances = card_redraw_chances
        self._dice_reroll_chances = dice_reroll_chances
        self._characters = characters
        self._hidden_statuses = hidden_statuses
        self._combat_statuses = combat_statuses
        self._summons = summons
        self._supports = supports
        self._dice = dice
        self._hand_cards = hand_cards
        self._deck_cards = deck_cards
        self._publicly_used_cards = publicly_used_cards
        self._publicly_gained_cards = publicly_gained_cards

    def factory(self) -> PlayerStateFactory:
        """ :returns: a factory for the current player state. """
        return PlayerStateFactory(self)

    def get_phase(self) -> Act:
        """ :returns: the (player) phase the player is in. """
        return self._phase

    def get_consec_action(self) -> bool:
        """
        :returns: if the player can make consecutive actions before the opponent
                  makes a move.
        """
        return self._consec_action

    def get_card_redraw_chances(self) -> int:
        """
        :returns: if the player can make consecutive actions before the opponent
                  makes a move.
        """
        return self._card_redraw_chances

    def get_dice_reroll_chances(self) -> int:
        """
        :returns: the number of chances to reroll dices.
        """
        return self._dice_reroll_chances

    def get_characters(self) -> Characters:
        """
        :returns: the characters the player have.
        """
        return self._characters

    def get_hidden_statuses(self) -> sts.Statuses:
        """
        :returns: the hidden statuses of the player. Typically holds information
                  that are invisible but useful in the game.
        """
        return self._hidden_statuses

    def get_combat_statuses(self) -> sts.Statuses:
        """ :returns: the combat statuses of the player.  """
        return self._combat_statuses

    def get_summons(self) -> Summons:
        """ :returns: the summons of the player.  """
        return self._summons

    def get_supports(self) -> Supports:
        """ :returns: the supports of the player.  """
        return self._supports

    def get_dice(self) -> ActualDice:
        """ :returns: the dice of the player.  """
        return self._dice

    def get_hand_cards(self) -> Cards:
        """ :returns: the hand cards of the player.  """
        return self._hand_cards

    def get_deck_cards(self) -> Cards:
        """ :returns: the deck cards that will be drawn in the future.  """
        return self._deck_cards

    def get_publicly_used_cards(self) -> Cards:
        """ :returns: the cards publicly used by the player. """
        return self._publicly_used_cards

    def get_publicly_gained_cards(self) -> Cards:
        """ :returns: the cards publicly gained by the player. """
        return self._publicly_gained_cards

    def get_active_character(self) -> None | chr.Character:
        """ :returns: the active character. `None` is returned if there isn't one. """
        return self._characters.get_active_character()

    def just_get_active_character(self) -> chr.Character:
        """ :returns: the active character. Exception is thrown if there isn't one. """
        return self._characters.just_get_active_character()

    def in_action_phase(self) -> bool:
        """ :returns: `True` if the player is in Action Phase. """
        return self._phase is Act.ACTION_PHASE

    def in_passive_wait_phase(self) -> bool:
        """ :returns: `True` if the player is in Passive Wait Phase. """
        return self._phase is Act.PASSIVE_WAIT_PHASE

    def in_active_wait_phase(self) -> bool:
        """ :returns: `True` if the player is in Active Wait Phase. """
        return self._phase is Act.ACTIVE_WAIT_PHASE

    def in_end_phase(self) -> bool:
        """ :returns: `True` if the player is in End Phase. """
        return self._phase is Act.END_PHASE

    def is_mine(self, object: chr.Character | sp.Support) -> bool:
        """ :returns: `True` if the `object` belongs to the player. """
        if isinstance(object, chr.Character):
            return self._characters.get_id(object) is not None
        elif isinstance(object, sp.Support):
            support = self._supports.find(type(object), object.sid)
            return support == object
        else:
            raise NotImplementedError

    def defeated(self) -> bool:
        """ :returns: `True` if the player is defeated. """
        return self._characters.all_defeated()

    def hide_secrets(self) -> PlayerState:
        """
        :returns: the same player but hides cards and dice. So opponent agent
                  cannot cheat with extra information.

        Cards are hidden by replacing them all with `OmniCard`.

        Dices are hidden by replacing them all with `ANY`. (Note this makes
        the new ActualDice invalid)
        """
        def hide_support(supports: Supports) -> Supports:
            for support in supports:
                if support.has_perspective_view():
                    supports = supports.update_support(support.perspective_view(), override=True)
            return supports

        return self.factory().f_hand_cards(
            lambda hcs: hcs.hide_all()
        ).f_deck_cards(
            lambda dcs: dcs.hide_all()
        ).f_dice(
            lambda d: d.hide_all()
        ).f_supports(
            hide_support
        ).build()

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        Encode the player state into a list of integers.
        """
        basics = [
            self._phase.value,
            int(self._consec_action),
            self._card_redraw_chances,
            self._dice_reroll_chances,
        ]
        return list(chain(
            basics,
            self._dice.encoding(encoding_plan),
            self._hand_cards.encoding(encoding_plan),
            self._deck_cards.encoding(encoding_plan),
            self._publicly_used_cards.encoding(encoding_plan),
            self._publicly_gained_cards.encoding(encoding_plan),
            self._characters.encoding(encoding_plan),
            self._hidden_statuses.encoding(encoding_plan, encoding_plan.PLAYER_HIDDEN_FIXED_LEN),
            self._combat_statuses.encoding(encoding_plan, encoding_plan.PLAYER_COMBAT_FIXED_LEN),
            self._summons.encoding(encoding_plan),
            self._supports.encoding(encoding_plan),
        ))

    def extract_deck(self) -> Deck:
        """
        :returns: the best estimation of the deck of the player.
        """
        from ..card.card import OmniCard
        from ..deck import FrozenDeck, MutableDeck

        empty_deck = FrozenDeck(
            chars=tuple([type(char) for char in self._characters]),
            cards=HashableDict()
        )
        cards = self._deck_cards + self._hand_cards + self._publicly_used_cards
        return MutableDeck(
            chars=[
                type(char) for char in self._characters
            ],
            cards={
                card: cards[card]
                for card in cards
                if card is not OmniCard and card.valid_in_deck(empty_deck)
            },
        )

    @classmethod
    def example_player(cls, mode: Mode) -> Self:
        """
        :returns: a random initial player state under the `mode`.
        """
        from ..card.card import ArcaneLegendCard
        from ..deck import FrozenDeck
        from ..helper.hashable_dict import HashableDict
        cards = mode.all_cards()
        chars = mode.all_chars()
        import random
        selected_chars = random.sample(list(chars), k=3)
        char_deck = FrozenDeck(chars=tuple(selected_chars), cards=HashableDict())
        cards_pool = []
        for card in cards:
            if not card.valid_in_deck(char_deck):
                continue
            if isinstance(card, ArcaneLegendCard):
                cards_pool.append(card)
            else:
                cards_pool.extend([card] * 2)
        selected_cards = random.sample(cards_pool, k=mode.deck_cards_requirement())
        return cls(
            phase=Act.PASSIVE_WAIT_PHASE,
            consec_action=False,
            card_redraw_chances=0,
            dice_reroll_chances=0,
            characters=Characters.from_default(
                tuple(char.from_default(i + 1) for i, char in enumerate(selected_chars))
            ),
            hidden_statuses=mode.player_default_hidden_statuses(),
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            dice=ActualDice({}),
            hand_cards=Cards({}),
            deck_cards=Cards(Counter(selected_cards)),
            publicly_used_cards=Cards({}),
            publicly_gained_cards=Cards({}),
        )

    @classmethod
    def from_chars_cards(cls, mode: Mode, characters: Characters, cards: Cards) -> Self:
        """
        :returns: the initial state of a player under `mode` with `characters` and `cards`.
        """
        return cls(
            phase=Act.PASSIVE_WAIT_PHASE,
            consec_action=False,
            card_redraw_chances=0,
            dice_reroll_chances=0,
            characters=characters,
            hidden_statuses=mode.player_default_hidden_statuses(),
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            dice=ActualDice({}),
            hand_cards=Cards({}),
            deck_cards=cards,
            publicly_used_cards=Cards({}),
            publicly_gained_cards=Cards({}),
        )

    @classmethod
    def from_deck(cls, mode: Mode, deck: Deck) -> Self:
        """
        :returns: the initial state of a player under `mode` with `deck`.
        """
        return cls(
            phase=Act.PASSIVE_WAIT_PHASE,
            consec_action=False,
            card_redraw_chances=0,
            dice_reroll_chances=0,
            characters=Characters.from_iterable(deck.chars),
            hidden_statuses=mode.player_default_hidden_statuses(),
            combat_statuses=sts.Statuses(()),
            summons=Summons((), mode.summons_limit()),
            supports=Supports((), mode.supports_limit()),
            dice=ActualDice({}),
            hand_cards=Cards({}),
            deck_cards=Cards(deck.cards),
            publicly_used_cards=Cards({}),
            publicly_gained_cards=Cards({}),
        )

    def _all_unique_data(self) -> tuple:
        return (
            self._phase,
            self._consec_action,
            self._card_redraw_chances,
            self._dice_reroll_chances,
            self._characters,
            self._hidden_statuses,
            self._combat_statuses,
            self._summons,
            self._supports,
            self._dice,
            self._hand_cards,
            self._deck_cards,
            self._publicly_used_cards,
            self._publicly_gained_cards,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayerState):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, _) -> Self:
        return self

    def dict_str(self) -> dict[str, Union[dict, str, list[str]]]:
        return {
            "Phase": self._phase.name,
            "Consecutive Action": str(self._consec_action),
            "Card/Dice Redraw Chances": f"{self._card_redraw_chances}/{self._dice_reroll_chances}",
            "Characters": self._characters.dict_str(),
            "Hidden Statuses": self._hidden_statuses.dict_str(),
            "Combat Statuses": self._combat_statuses.dict_str(),
            "Summons": self._summons.dict_str(),
            "Supports": self._supports.dict_str(),
            "Dice": self._dice.dict_str(),
            "Hand Cards": self._hand_cards.dict_str(),
            "Deck Cards": self._deck_cards.dict_str(),
            "Publicly Used Cards": self._publicly_used_cards.dict_str(),
            "Publicly Gained Cards": self._publicly_gained_cards.dict_str(),
        }


class PlayerStateFactory:
    def __init__(self, player_state: PlayerState) -> None:
        self._phase = player_state.get_phase()
        self._consec_action = player_state.get_consec_action()
        self._card_redraw_chances = player_state.get_card_redraw_chances()
        self._dice_reroll_chances = player_state.get_dice_reroll_chances()
        self._characters = player_state.get_characters()
        self._hidden_statuses = player_state.get_hidden_statuses()
        self._combat_statuses = player_state.get_combat_statuses()
        self._summons = player_state.get_summons()
        self._supports = player_state.get_supports()
        self._dice = player_state.get_dice()
        self._hand_cards = player_state.get_hand_cards()
        self._deck_cards = player_state.get_deck_cards()
        self._publicly_used_cards = player_state.get_publicly_used_cards()
        self._publicly_gained_cards = player_state.get_publicly_gained_cards()

    def phase(self, phase: Act) -> PlayerStateFactory:
        self._phase = phase
        return self

    def consec_action(self, consec_action: bool) -> PlayerStateFactory:
        self._consec_action = consec_action
        return self

    def f_consec_action(self, f: Callable[[bool], bool]) -> PlayerStateFactory:
        return self.consec_action(f(self._consec_action))

    def card_redraw_chances(self, chances: int) -> PlayerStateFactory:
        self._card_redraw_chances = chances
        return self

    def f_card_redraw_chances(self, f: Callable[[int], int]) -> PlayerStateFactory:  # pragma: no cover
        return self.card_redraw_chances(f(self._card_redraw_chances))

    def dice_reroll_chances(self, chances: int) -> PlayerStateFactory:
        self._dice_reroll_chances = chances
        return self

    def f_dice_reroll_chances(self, f: Callable[[int], int]) -> PlayerStateFactory:  # pragma: no cover
        return self.dice_reroll_chances(f(self._dice_reroll_chances))

    def characters(self, characters: Characters) -> PlayerStateFactory:
        self._characters = characters
        return self

    def f_characters(self, f: Callable[[Characters], Characters]) -> PlayerStateFactory:
        self._characters = f(self._characters)
        return self

    def hidden_statuses(self, hidden_statuses: sts.Statuses) -> PlayerStateFactory:
        self._hidden_statuses = hidden_statuses
        return self

    def f_hidden_statuses(self, f: Callable[[sts.Statuses], sts.Statuses]) -> PlayerStateFactory:
        return self.hidden_statuses(f(self._hidden_statuses))

    def combat_statuses(self, combat_statuses: sts.Statuses) -> PlayerStateFactory:
        self._combat_statuses = combat_statuses
        return self

    def f_combat_statuses(self, f: Callable[[sts.Statuses], sts.Statuses]) -> PlayerStateFactory:
        return self.combat_statuses(f(self._combat_statuses))

    def summons(self, summons: Summons) -> PlayerStateFactory:
        self._summons = summons
        return self

    def f_summons(self, f: Callable[[Summons], Summons]) -> PlayerStateFactory:
        return self.summons(f(self._summons))

    def supports(self, supports: Supports) -> PlayerStateFactory:
        self._supports = supports
        return self

    def f_supports(self, f: Callable[[Supports], Supports]) -> PlayerStateFactory:
        return self.supports(f(self._supports))

    def dice(self, dice: ActualDice) -> PlayerStateFactory:
        self._dice = dice
        return self

    def f_dice(self, f: Callable[[ActualDice], ActualDice]) -> PlayerStateFactory:
        return self.dice(f(self._dice))

    def hand_cards(self, cards: Cards) -> PlayerStateFactory:
        self._hand_cards = cards
        return self

    def f_hand_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.hand_cards(f(self._hand_cards))

    def deck_cards(self, cards: Cards) -> PlayerStateFactory:
        self._deck_cards = cards
        return self

    def f_deck_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.deck_cards(f(self._deck_cards))

    def publicly_used_cards(self, cards: Cards) -> PlayerStateFactory:
        self._publicly_used_cards = cards
        return self

    def f_publicly_used_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.publicly_used_cards(f(self._publicly_used_cards))

    def publicly_gained_cards(self, cards: Cards) -> PlayerStateFactory:
        self._publicly_gained_cards = cards
        return self

    def f_publicly_gained_cards(self, f: Callable[[Cards], Cards]) -> PlayerStateFactory:
        return self.publicly_gained_cards(f(self._publicly_gained_cards))

    def build(self) -> PlayerState:
        return PlayerState(
            phase=self._phase,
            consec_action=self._consec_action,
            card_redraw_chances=self._card_redraw_chances,
            dice_reroll_chances=self._dice_reroll_chances,
            characters=self._characters,
            hidden_statuses=self._hidden_statuses,
            combat_statuses=self._combat_statuses,
            summons=self._summons,
            supports=self._supports,
            dice=self._dice,
            hand_cards=self._hand_cards,
            deck_cards=self._deck_cards,
            publicly_used_cards=self._publicly_used_cards,
            publicly_gained_cards=self._publicly_gained_cards,
        )
