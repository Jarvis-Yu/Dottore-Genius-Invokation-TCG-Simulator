from __future__ import annotations
from dataclasses import replace
from typing import Callable, Optional, TYPE_CHECKING

from .. import mode as md
from ..action import action as act
from ..action import action_generator as acg
from ..effect import effect as eft
from ..phase import game_end_phase as gep
from ..phase import phase as ph
from ..state import player_state as ps

from ..action.action import PlayerAction
from ..character.character import Character
from ..character.character_skill_enum import CharacterSkill
from ..dices import ActualDices
from ..effect.enums import ZONE
from ..effect.structs import StaticTarget
from ..effect.effect_stack import EffectStack
from ..effect.enums import ZONE
from ..effect.structs import StaticTarget
from ..element.element import Element
from ..event.event import *
from ..helper.level_print import level_print, level_print_single, INDENT
from ..helper.quality_of_life import case_val
from .enums import PID
from ..status.status_processing import StatusProcessing
from ..status.enums import PREPROCESSABLES
from ..support.support import Support

if TYPE_CHECKING:
    from ..action.types import DecidedChoiceType, GivenChoiceType


class GameState:

    def __init__(
        self,
        mode: md.Mode,
        phase: ph.Phase,
        round: int,
        active_player_id: PID,
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
        self._swap_checker = SwapChecker(self)
        self._skill_checker = SkillChecker(self)
        self._elem_tuning_checker = ElementalTuningChecker(self)

    @classmethod
    def from_default(cls):
        mode = md.DefaultMode()
        return cls(
            mode=mode,
            phase=mode.card_select_phase(),
            round=0,
            active_player_id=PID.P1,
            player1=ps.PlayerState.examplePlayer(mode),
            player2=ps.PlayerState.examplePlayer(mode),
            effect_stack=EffectStack(()),
        )

    def factory(self):
        return GameStateFactory(self)

    def get_mode(self) -> md.Mode:
        return self._mode

    def get_phase(self) -> ph.Phase:
        return self._phase

    def get_round(self) -> int:
        return self._round

    def get_active_player_id(self) -> PID:
        return self._active_player_id

    def get_effect_stack(self) -> EffectStack:
        return self._effect_stack

    def get_player1(self) -> ps.PlayerState:
        return self._player1

    def get_player2(self) -> ps.PlayerState:
        return self._player2

    def get_pid(self, player: ps.PlayerState) -> PID:
        if player is self._player1:
            return PID.P1
        elif player is self._player2:
            return PID.P2
        else:
            raise Exception("player unknown")

    def get_player(self, player_id: PID) -> ps.PlayerState:
        if player_id.is_player1():
            return self._player1
        elif player_id.is_player2():
            return self._player2
        else:
            raise Exception("player_id unknown")

    def get_other_player(self, player_id: PID) -> ps.PlayerState:
        if player_id.is_player1():
            return self._player2
        elif player_id.is_player2():
            return self._player1
        else:
            raise Exception("player_id unknown")

    def swap_checker(self) -> SwapChecker:
        return self._swap_checker

    def skill_checker(self) -> SkillChecker:
        return self._skill_checker

    def elem_tuning_checker(self) -> ElementalTuningChecker:
        return self._elem_tuning_checker

    def belongs_to(self, object: Character | Support) -> None | PID:
        """ int in object type is just place holder """
        if self._player1.is_mine(object):
            return PID.P1
        elif self._player2.is_mine(object):
            return PID.P2
        else:
            return None

    def get_target(self, target: StaticTarget) -> None | Character | Support:
        player = self.get_player(target.pid)
        if target.zone is ZONE.CHARACTERS:
            return player.get_characters().get_character(target.id)
        elif target.zone is ZONE.SUPPORTS:
            return player.get_supports().find_by_sid(target.id)
        else:
            raise Exception("Not Implemented Yet")
        return None

    def get_character_target(self, target: StaticTarget) -> None | Character:
        character = self.get_target(target)
        if not isinstance(character, Character):
            return None
        return character

    def waiting_for(self) -> Optional[PID]:
        return self._phase.waiting_for(self)

    def step(self) -> GameState:
        return self._phase.step(self)

    def action_step(self, pid: PID, action: PlayerAction) -> Optional[GameState]:
        """
        Returns None if the action is illegal or undefined
        """
        return self._phase.step_action(self, pid, action)

    def get_winner(self) -> Optional[PID]:
        assert self.game_end()
        if self.get_player1().defeated():
            return PID.P2
        elif self.get_player2().defeated():
            return PID.P1
        else:
            return None

    def game_end(self) -> bool:
        return isinstance(self._phase, gep.GameEndPhase)

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
        if self is other:
            return True
        if not isinstance(other, GameState):
            return False
        return self._all_unique_data() == other._all_unique_data()

    def __hash__(self) -> int:
        return hash(self._all_unique_data())

    def __str__(self) -> str:
        from ..helper.level_print import GamePrinter
        return GamePrinter.dict_game_printer(self.dict_str())

    def to_string(self, indent: int = 0) -> str:
        new_indent = indent + INDENT
        return level_print({
            "Mode": self._mode.to_string(new_indent),
            "Phase": self._phase.to_string(new_indent),
            "Round": level_print_single(str(self._round), new_indent),
            "Active Player": level_print_single(str(self._active_player_id), new_indent),
            "Player1": self._player1.to_string(new_indent),
            "Player2": self._player2.to_string(new_indent),
            "Effects": self._effect_stack.to_string(new_indent),
        }, indent)

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

    def active_player_id(self, pid: PID) -> GameStateFactory:
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

    def player(self, pid: PID, new_player: ps.PlayerState) -> GameStateFactory:
        if pid is PID.P1:
            return self.player1(new_player)
        elif pid is PID.P2:
            return self.player2(new_player)
        else:
            raise Exception("player_id unknown")

    def f_player(self, pid: PID, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        if pid is PID.P1:
            return self.player1(f(self._player1))
        elif pid is PID.P2:
            return self.player2(f(self._player2))
        else:
            raise Exception("player_id unknown")

    def other_player(self, pid: PID, new_player: ps.PlayerState) -> GameStateFactory:
        if pid is PID.P1:
            return self.player2(new_player)
        elif pid is PID.P2:
            return self.player1(new_player)
        else:
            raise Exception("player_id unknown")

    def f_other_player(self, pid: PID, f: Callable[[ps.PlayerState], ps.PlayerState]) -> GameStateFactory:
        if pid is PID.P1:
            return self.player2(f(self._player2))
        elif pid is PID.P2:
            return self.player1(f(self._player1))
        else:
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


class SwapChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def _choices_helper(
            self,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = self._game_state
        pid = action_generator.pid

        action = action_generator.action
        if not action_generator._action_filled():
            assert type(action) is act.SwapAction \
                or type(action) is act.DeathSwapAction
            swappable_char_ids = [
                char.get_id()
                for char in game_state.get_player(pid).get_characters()
                if self.swap_details(pid, char.get_id()) is not None
            ]
            return tuple(
                char_id
                for char_id in swappable_char_ids
            )

        assert type(action) is act.SwapAction
        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            swap_details = self.swap_details(pid, action.char_id)
            assert swap_details is not None
            _, dices_cost = swap_details
            assert dices_cost is not None
            return dices_cost

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    def _fill_helper(
        self,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        action = action_generator.action
        assert type(action) is act.SwapAction \
            or type(action) is act.DeathSwapAction
        if action.char_id is None:
            assert type(player_choice) is int
            return replace(
                action_generator,
                action=replace(action, char_id=player_choice),
            )

        assert action_generator._action_filled()
        assert type(action) is act.SwapAction

        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            assert isinstance(player_choice, ActualDices)
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    def action_generator(
            self,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        if not self.swappable(pid):
            return None
        if self.should_death_swap():
            return acg.ActionGenerator(
                game_state=self._game_state,
                pid=pid,
                action=act.DeathSwapAction._all_none(),
                instruction=None,
                _choices_helper=self._choices_helper,
                _fill_helper=self._fill_helper,
            )
        else:
            return acg.ActionGenerator(
                game_state=self._game_state,
                pid=pid,
                action=act.SwapAction._all_none(),
                instruction=act.DiceOnlyInstruction._all_none(),
                _choices_helper=self._choices_helper,
                _fill_helper=self._fill_helper,
            )

    def should_death_swap(self) -> bool:
        effect_stack = self._game_state.get_effect_stack()
        return effect_stack.is_not_empty() \
            and isinstance(effect_stack.peek(), eft.DeathSwapPhaseStartEffect)

    def swappable(
            self,
            pid: PID,
    ) -> bool:
        return any(
            self.swap_details(pid, char.get_id()) is not None
            for char in self._game_state.get_player(pid).get_characters()
        )

    def swap_details(
            self,
            pid: PID,
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
            item=GameEvent(
                target=StaticTarget(
                    pid=pid,
                    zone=ZONE.CHARACTERS,
                    id=char_id,
                ),
                event_type=EventType.SWAP,
                event_speed=game_state.get_mode().swap_speed(),
                dices_cost=game_state.get_mode().swap_cost(),
            ),
            pp_type=PREPROCESSABLES.SWAP,
        )
        assert isinstance(swap_action, GameEvent)
        if game_state.get_player(pid).get_dices().loosely_satisfy(swap_action.dices_cost):
            return swap_action.event_speed, swap_action.dices_cost
        else:
            return None

    def valid_action(
            self,
            pid: PID,
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
                item=GameEvent(
                    target=StaticTarget(
                        pid=pid,
                        zone=ZONE.CHARACTERS,
                        id=action.char_id,
                    ),
                    event_type=EventType.SWAP,
                    event_speed=game_state.get_mode().swap_speed(),
                    dices_cost=game_state.get_mode().swap_cost(),
                ),
                pp_type=PREPROCESSABLES.SWAP,
            )
            assert isinstance(swap_action, GameEvent)
            instruction_dices = action.instruction.dices
            player_dices = game_state.get_player(pid).get_dices()
            return case_val(
                (player_dices - instruction_dices).is_legal()
                and instruction_dices.just_satisfy(swap_action.dices_cost),
                (new_game_state, swap_action.event_speed),
                None
            )
        raise Exception("action ({action}) is not expected to be passed in")


class SkillChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def _choices_helper(
            self,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = self._game_state
        pid = action_generator.pid
        active_character = game_state.get_player(pid).just_get_active_character()

        action = action_generator.action
        assert type(action) is act.SkillAction
        if action.skill is None:
            skills = active_character.skills()
            return tuple(
                skill
                for skill in skills
                if self.usable(pid, active_character.get_id(), skill) is not None
            )

        assert action_generator._action_filled()
        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            retval = self.usable(pid, active_character.get_id(), action.skill)
            assert retval is not None
            _, dices = retval
            return dices

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    def _fill_helper(
        self,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        action = action_generator.action
        assert type(action) is act.SkillAction
        if action.skill is None:
            assert type(player_choice) is CharacterSkill
            return replace(
                action_generator,
                action=replace(action, skill=player_choice),
            )

        instruction = action_generator.instruction
        assert type(instruction) is act.DiceOnlyInstruction
        if instruction.dices is None:
            assert type(player_choice) is ActualDices
            return replace(
                action_generator,
                instruction=replace(instruction, dices=player_choice),
            )

        raise Exception("Not Reached!")

    def action_generator(
            self,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        active_character = self._game_state.get_player(pid).just_get_active_character()
        if not active_character.can_cast_skill():
            return None

        has_castable_skill = any(
            self.usable(pid, active_character.get_id(), skill) is not None
            for skill in active_character.skills()
        )
        if not has_castable_skill:
            return None

        return acg.ActionGenerator(
            game_state=self._game_state,
            pid=pid,
            action=act.SkillAction._all_none(),
            instruction=act.DiceOnlyInstruction._all_none(),
            _choices_helper=self._choices_helper,
            _fill_helper=self._fill_helper,
        )

    def usable(
            self,
            pid: PID,
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
            item=GameEvent(
                target=StaticTarget(
                    pid=pid,
                    zone=ZONE.CHARACTERS,
                    id=char_id,
                ),
                event_type=skill_type.to_event_type(),
                event_speed=EventSpeed.COMBAT_ACTION,
                dices_cost=character.skill_cost(skill_type),
            ),
            pp_type=PREPROCESSABLES.SKILL,
        )
        assert isinstance(skill_event, GameEvent)
        if game_state.get_player(pid).get_dices().loosely_satisfy(skill_event.dices_cost):
            return new_game_state, skill_event.dices_cost
        else:
            return None

    def valid_action(
            self,
            pid: PID,
            action: act.SkillAction,
    ) -> None | GameState:
        game_state = self._game_state
        skill_type = action.skill
        character = game_state.get_player(pid).get_active_character()
        if character is None \
                or not character.can_cast_skill() \
                or skill_type not in character.skills():
            return None
        if skill_type is CharacterSkill.ELEMENTAL_BURST \
                and character.get_energy() < character.get_max_energy():
            return None
        game_state, skill_event = StatusProcessing.preprocess_by_all_statuses(
            game_state=game_state,
            pid=pid,
            item=GameEvent(
                target=StaticTarget(
                    pid=pid,
                    zone=ZONE.CHARACTERS,
                    id=character.get_id(),
                ),
                event_type=skill_type.to_event_type(),
                event_speed=EventSpeed.COMBAT_ACTION,
                dices_cost=character.skill_cost(skill_type),
            ),
            pp_type=PREPROCESSABLES.SKILL,
        )
        assert isinstance(skill_event, GameEvent)
        if action.instruction.dices.just_satisfy(skill_event.dices_cost):
            return game_state
        else:
            return None


class ElementalTuningChecker:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def usable(self, pid: PID, elem: None | Element = None) -> bool:
        game_state = self._game_state
        if not (type(game_state.get_phase()) == type(game_state.get_mode().action_phase())
                or game_state.get_active_player_id() is pid):
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

    def _choices_helper(
            self,
            action_generator: acg.ActionGenerator,
    ) -> GivenChoiceType:
        game_state = self._game_state
        pid = action_generator.pid

        action = action_generator.action
        assert type(action) is act.ElementalTuningAction

        if action.card is None:
            return tuple(card for card in game_state.get_player(pid).get_hand_cards())

        active_character = game_state.get_player(pid).just_get_active_character()
        if action.dice_elem is None:
            return tuple(
                elem
                for elem in game_state.get_player(pid).get_dices()
                if elem is not Element.OMNI and elem is not active_character.element()
            )

        raise Exception(
            "Not Reached! Should be called when there is something to fill. action_generator:\n"
            + f"{action_generator}"
        )

    def _fill_helper(
        self,
        action_generator: acg.ActionGenerator,
        player_choice: DecidedChoiceType,
    ) -> acg.ActionGenerator:
        action = action_generator.action
        assert type(action) is act.ElementalTuningAction

        if action.card is None:
            assert issubclass(player_choice, cd.Card)  # type: ignore
            return replace(
                action_generator,
                action=replace(action, card=player_choice)
            )

        if action.dice_elem is None:
            assert type(player_choice) is Element
            return replace(
                action_generator,
                action=replace(action, dice_elem=player_choice)
            )

        raise Exception("Not Reached!")

    def action_generator(
            self,
            pid: PID,
    ) -> None | acg.ActionGenerator:
        if not self.usable(pid):
            return None

        return acg.ActionGenerator(
            game_state=self._game_state,
            pid=pid,
            action=act.ElementalTuningAction._all_none(),
            instruction=None,
            _choices_helper=self._choices_helper,
            _fill_helper=self._fill_helper,
        )
