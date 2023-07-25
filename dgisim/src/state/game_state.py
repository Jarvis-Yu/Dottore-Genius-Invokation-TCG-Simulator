from __future__ import annotations
from typing import Callable, cast, Optional
from typing_extensions import Self

from .. import mode as md
from ..action import action as act
from ..action import action_generator as acg
from ..effect import effect as eft
from ..phase import phase as ph
from ..state import player_state as ps

from ..action.action import PlayerAction
from ..card.card import Card
from ..character.character import Character
from ..character.enums import CharacterSkill
from ..dices import AbstractDices
from ..effect.enums import Zone
from ..effect.structs import StaticTarget
from ..effect.effect_stack import EffectStack
from ..effect.enums import Zone
from ..effect.structs import StaticTarget
from ..element import Element
from ..event import *
from ..helper.quality_of_life import case_val
from ..status.status_processing import StatusProcessing
from ..status.enums import Preprocessables
from ..summon.summon import Summon
from ..support.support import Support
from .enums import Pid

__all__ = [
    "GameState",
]


class GameState:
    """
    The class which represents a moment or a state of the game, containing all
    information required to proceed to the next game state.

    To proceed when the game doesn't require a player action at the moment,
    run step(), otherwise run action_step(player_action).

    To tell if a player action is required, run waiting_for().
    """

    def __init__(
        self,
        mode: md.Mode,
        phase: ph.Phase,
        round: int,
        active_player_id: Pid,
        player1: ps.PlayerState,
        player2: ps.PlayerState,
        effect_stack: EffectStack
    ):
        # REMINDER: don't forget to update factory when adding new fields
        self._mode = mode
        self._phase = phase
        self._round = round
        self._active_player_id = active_player_id
        self._player1 = player1
        self._player2 = player2
        self._effect_stack = effect_stack

        # checkers
        self._card_checker = CardChecker(self)
        self._swap_checker = SwapChecker(self)
        self._skill_checker = SkillChecker(self)
        self._elem_tuning_checker = ElementalTuningChecker(self)

    @classmethod
    def from_default(cls) -> Self:
        mode = md.DefaultMode()
        return cls(
            mode=mode,
            phase=mode.card_select_phase(),
            round=0,
            active_player_id=Pid.P1,
            player1=ps.PlayerState.example_player(mode),
            player2=ps.PlayerState.example_player(mode),
            effect_stack=EffectStack(()),
        )

    @classmethod
    def from_players(cls, mode: md.Mode, player1: ps.PlayerState, player2: ps.PlayerState) -> Self:
        return cls(  # pragma: no cover
            mode=mode,
            phase=mode.card_select_phase(),
            round=0,
            active_player_id=Pid.P1,
            player1=player1,
            player2=player2,
            effect_stack=EffectStack(()),
        )

    def factory(self) -> GameStateFactory:
        return GameStateFactory(self)

    def get_mode(self) -> md.Mode:
        return self._mode

    def get_phase(self) -> ph.Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_active_player_id(self) -> Pid:
        return self._active_player_id

    def get_effect_stack(self) -> EffectStack:
        return self._effect_stack

    def get_player1(self) -> ps.PlayerState:
        return self._player1

    def get_player2(self) -> ps.PlayerState:
        return self._player2

    def get_pid(self, player: ps.PlayerState) -> Pid:
        if player is self._player1:
            return Pid.P1
        elif player is self._player2:
            return Pid.P2
        else:  # pragma: no cover
            raise Exception("player unknown")

    def get_player(self, player_id: Pid) -> ps.PlayerState:
        if player_id.is_player1():
            return self._player1
        elif player_id.is_player2():
            return self._player2
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def get_other_player(self, player_id: Pid) -> ps.PlayerState:
        if player_id.is_player1():
            return self._player2
        elif player_id.is_player2():
            return self._player1
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def death_swapping(self, player_id: None | Pid = None) -> bool:
        from ..effect.effect import DeathSwapPhaseStartEffect
        return (
            self._effect_stack.is_not_empty()
            and isinstance(self._effect_stack.peek(), DeathSwapPhaseStartEffect)
            and (
                player_id is None
                or self.get_player(player_id).get_phase().is_action_phase()
            )
        )

    def card_checker(self) -> CardChecker:
        return self._card_checker

    def swap_checker(self) -> SwapChecker:
        return self._swap_checker

    def skill_checker(self) -> SkillChecker:
        return self._skill_checker

    def elem_tuning_checker(self) -> ElementalTuningChecker:
        return self._elem_tuning_checker

    def belongs_to(self, object: Character | Support) -> None | Pid:
        """ int in object type is just place holder """
        if self._player1.is_mine(object):
            return Pid.P1
        elif self._player2.is_mine(object):
            return Pid.P2
        else:  # pragma: no cover
            return None

    def get_target(self, target: StaticTarget) -> None | Character | Summon | Support:
        player = self.get_player(target.pid)
        if target.zone is Zone.CHARACTERS:
            return player.get_characters().get_character(cast(int, target.id))
        elif target.zone is Zone.SUMMONS:
            return player.get_summons().find(cast(type[Summon], target.id))
        elif target.zone is Zone.SUPPORTS:
            return player.get_supports().find_by_sid(cast(int, target.id))
        else:
            raise Exception("Not Reached!")

    def get_character_target(self, target: StaticTarget) -> None | Character:
        character = self.get_target(target)
        if not isinstance(character, Character):  # pragma: no cover
            return None
        return character

    def waiting_for(self) -> Optional[Pid]:
        return self._phase.waiting_for(self)

    def step(self) -> GameState:
        return self._phase.step(self)

    def action_step(self, pid: Pid, action: PlayerAction) -> Optional[GameState]:
        """
        Returns None if the action is illegal or undefined
        """
        return self._phase.step_action(self, pid, action)

    def action_generator(self, pid: Pid) -> None | acg.ActionGenerator:
        return self._phase.action_generator(self, pid)

    def get_winner(self) -> Optional[Pid]:
        assert self.game_end()
        if self.get_player1().defeated():
            return Pid.P2
        elif self.get_player2().defeated():
            return Pid.P1
        else:
            return None

    def game_end(self) -> bool:
        return type(self._phase) is type(self._mode.game_end_phase())

    def prespective_view(self, pid: Pid) -> GameState:
        return self.factory().f_player(
            pid.other(),
            lambda p: p.hide_cards()
        ).build()

    def _all_unique_data(self) -> tuple:
        return (
            self._phase,
            self._round,
            self._active_player_id,
            self._player1,
            self._player2,
            self._effect_stack,
            self._mode,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameState):
            return False
        return self is other or self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        from ..helper.level_print import GamePrinter
        return GamePrinter.dict_game_printer(self.dict_str())

    def dict_str(self) -> dict:
        return {
            "Mode": self._mode.dict_str(),
            "Phase": self._phase.dict_str(),
            "Round": str(self._round),
            "Active Player": str(self._active_player_id),
            "Player1": self._player1.dict_str(),
            "Player2": self._player2.dict_str(),
            "Effects": self._effect_stack.dict_str(),
        }


class GameStateFactory:
    def __init__(self, game_state: GameState):
        self._mode = game_state.get_mode()
        self._phase = game_state.get_phase()
        self._round = game_state.get_round()
        self._active_player = game_state.get_active_player_id()
        self._player1 = game_state.get_player1()
        self._player2 = game_state.get_player2()
        self._effect_stack = game_state.get_effect_stack()

    def mode(self, new_mode: md.Mode) -> GameStateFactory:
        self._mode = new_mode
        return self

    def phase(self, new_phase: ph.Phase) -> GameStateFactory:
        self._phase = new_phase
        return self

    def f_phase(self, f: Callable[[md.Mode], ph.Phase]) -> GameStateFactory:
        return self.phase(f(self._mode))

    def round(self, new_round: int) -> GameStateFactory:
        self._round = new_round
        return self

    def effect_stack(self, effect_stack: EffectStack) -> GameStateFactory:
        self._effect_stack = effect_stack
        return self

    def f_effect_stack(self, f: Callable[[EffectStack], EffectStack]) -> GameStateFactory:
        return self.effect_stack(f(self._effect_stack))

    def active_player_id(self, pid: Pid) -> GameStateFactory:
        self._active_player = pid
        return self

    def player1(self, new_player: ps.PlayerState) -> GameStateFactory:
        self._player1 = new_player
        return self

    def f_player1(self, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        return self.player1(f(self._player1))

    def player2(self, new_player: ps.PlayerState) -> GameStateFactory:
        self._player2 = new_player
        return self

    def f_player2(self, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        return self.player2(f(self._player2))

    def player(self, pid: Pid, new_player: ps.PlayerState) -> GameStateFactory:
        if pid is Pid.P1:
            return self.player1(new_player)
        elif pid is Pid.P2:
            return self.player2(new_player)
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def f_player(self, pid: Pid, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        if pid is Pid.P1:
            return self.player1(f(self._player1))
        elif pid is Pid.P2:
            return self.player2(f(self._player2))
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def other_player(self, pid: Pid, new_player: ps.PlayerState) -> GameStateFactory:
        if pid is Pid.P1:
            return self.player2(new_player)
        elif pid is Pid.P2:
            return self.player1(new_player)
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def f_other_player(self, pid: Pid, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        if pid is Pid.P1:
            return self.player2(f(self._player2))
        elif pid is Pid.P2:
            return self.player1(f(self._player1))
        else:  # pragma: no cover
            raise Exception("player_id unknown")

    def build(self) -> GameState:
        return GameState(
            mode=self._mode,
            phase=self._phase,
            round=self._round,
            active_player_id=self._active_player,
            effect_stack=self._effect_stack,
            player1=self._player1,
            player2=self._player2,
        )


class CardChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def usable(self, pid: Pid, card_type: type[Card]) -> None | acg.ActionGenerator:
        return card_type.action_generator(self._game_state, pid)

    def playable(self, pid: Pid) -> bool:
        """ Returns true if any card is playable """
        return any(
            card_type.strictly_usable(self._game_state, pid)
            for card_type in self._game_state.get_player(pid).get_hand_cards()
        )


class SwapChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def should_death_swap(self) -> bool:
        effect_stack = self._game_state.get_effect_stack()
        return effect_stack.is_not_empty() \
            and isinstance(effect_stack.peek(), eft.DeathSwapPhaseStartEffect)

    def swappable(
            self,
            pid: Pid,
    ) -> bool:
        """ Returns true if a swap to any character is available """
        return any(
            self.swap_details(pid, char.get_id()) is not None
            for char in self._game_state.get_player(pid).get_characters()
        )

    def swap_details(
            self,
            pid: Pid,
            char_id: int,
    ) -> None | tuple[EventSpeed, None | AbstractDices]:
        game_state = self._game_state
        selected_char = game_state.get_player(pid).get_characters().get_character(char_id)
        active_character_id = game_state.get_player(pid).get_characters().get_active_character_id()
        if selected_char is None \
                or selected_char.defeated() \
                or selected_char.get_id() == active_character_id:
            return None

        if self.should_death_swap():
            return EventSpeed.FAST_ACTION, None

        # Check if player can afford Normal Swap
        _, swap_action = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            pp_type=Preprocessables.SWAP,
            item=ActionPEvent(
                source=StaticTarget(
                    pid=pid,
                    zone=Zone.CHARACTERS,
                    id=char_id,
                ),
                event_type=EventType.SWAP,
                event_speed=game_state.get_mode().swap_speed(),
                dices_cost=game_state.get_mode().swap_cost(),
            ),
        )
        assert isinstance(swap_action, ActionPEvent)
        if game_state.get_player(pid).get_dices().loosely_satisfy(swap_action.dices_cost):
            return swap_action.event_speed, swap_action.dices_cost
        else:
            return None

    def valid_action(
            self,
            pid: Pid,
            action: act.SwapAction | act.DeathSwapAction,
    ) -> None | tuple[GameState, EventSpeed]:
        """
        Return None if the action is invalid,
        otherwise return the GameState after preprocessing the swap event.
        """
        game_state = self._game_state
        selected_char = game_state.get_player(
            pid
        ).get_characters().get_character(action.char_id)
        active_character_id = game_state.get_player(pid).get_characters().get_active_character_id()
        if selected_char is None \
                or selected_char.defeated() \
                or selected_char.get_id() == active_character_id:
            return None
        if isinstance(action, act.DeathSwapAction):
            swap_details = self.swap_details(
                pid=pid,
                char_id=action.char_id,
            )
            return case_val(
                swap_details is not None,
                (game_state, EventSpeed.FAST_ACTION),
                None,
            )
        elif isinstance(action, act.SwapAction):
            new_game_state, swap_action = StatusProcessing.preprocess_by_all_statuses(
                game_state=game_state,
                pid=pid,
                pp_type=Preprocessables.SWAP,
                item=ActionPEvent(
                    source=StaticTarget(
                        pid=pid,
                        zone=Zone.CHARACTERS,
                        id=action.char_id,
                    ),
                    event_type=EventType.SWAP,
                    event_speed=game_state.get_mode().swap_speed(),
                    dices_cost=game_state.get_mode().swap_cost(),
                ),
            )
            assert isinstance(swap_action, ActionPEvent)
            instruction_dices = action.instruction.dices
            player_dices = game_state.get_player(pid).get_dices()
            return case_val(
                (player_dices - instruction_dices).is_legal()
                and instruction_dices.just_satisfy(swap_action.dices_cost),
                (new_game_state, swap_action.event_speed),
                None
            )
        raise Exception("action ({action}) is not expected to be passed in")  # pragma: no cover


class SkillChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def usable(
            self,
            pid: Pid,
            char_id: int,
            skill_type: CharacterSkill,
    ) -> None | tuple[GameState, AbstractDices]:
        game_state = self._game_state
        character = game_state.get_player(pid).get_characters().get_character(char_id)
        if character is None \
                or not character.can_cast_skill() \
                or skill_type not in character.skills():
            return None
        if skill_type is CharacterSkill.ELEMENTAL_BURST \
                and character.get_energy() < character.get_max_energy():
            return None
        new_game_state, skill_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            pp_type=Preprocessables.SKILL,
            item=ActionPEvent(
                source=StaticTarget(
                    pid=pid,
                    zone=Zone.CHARACTERS,
                    id=char_id,
                ),
                event_type=skill_type.to_event_type(),
                event_speed=EventSpeed.COMBAT_ACTION,
                dices_cost=character.skill_cost(skill_type),
            ),
        )
        assert isinstance(skill_event, ActionPEvent)
        if game_state.get_player(pid).get_dices().loosely_satisfy(skill_event.dices_cost):
            return new_game_state, skill_event.dices_cost
        else:
            return None

    def skillable(
            self,
            pid: Pid
    ) -> bool:
        active_character_id = self._game_state.get_player(pid).just_get_active_character().get_id()
        return any(
            self.usable(pid, active_character_id, skill_type)
            for skill_type in CharacterSkill
        )

    def valid_action(
            self,
            pid: Pid,
            action: act.SkillAction,
    ) -> None | GameState:
        game_state = self._game_state
        skill_type = action.skill
        character = game_state.get_player(pid).get_active_character()
        if character is None \
                or not character.can_cast_skill() \
                or skill_type not in character.skills():  # pragma: no cover
            return None
        if skill_type is CharacterSkill.ELEMENTAL_BURST \
                and character.get_energy() < character.get_max_energy():  # pragma: no cover
            return None
        game_state, skill_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            pp_type=Preprocessables.SKILL,
            item=ActionPEvent(
                source=StaticTarget(
                    pid=pid,
                    zone=Zone.CHARACTERS,
                    id=character.get_id(),
                ),
                event_type=skill_type.to_event_type(),
                event_speed=EventSpeed.COMBAT_ACTION,
                dices_cost=character.skill_cost(skill_type),
            ),
        )
        assert isinstance(skill_event, ActionPEvent)
        paid_dices = action.instruction.dices
        if paid_dices.just_satisfy(skill_event.dices_cost) \
                and (game_state.get_player(pid).get_dices() - paid_dices).is_legal():
            return game_state
        else:
            return None


class ElementalTuningChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def usable(self, pid: Pid, elem: None | Element = None) -> bool:
        game_state = self._game_state
        if not (type(game_state.get_phase()) == type(game_state.get_mode().action_phase())
                or game_state.get_active_player_id() is pid):  # pragma: no cover
            return False
        player = game_state.get_player(pid)
        active_character = player.get_active_character()
        assert active_character is not None
        active_character_elem = active_character.element()
        dices = player.get_dices()
        return (
            player.get_hand_cards().not_empty()
            and dices[Element.OMNI] + dices[active_character_elem] < dices.num_dices()
            and (elem is None or dices[elem] > 0)
        )
