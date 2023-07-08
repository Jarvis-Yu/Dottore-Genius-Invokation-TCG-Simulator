from __future__ import annotations
from typing import Callable, TYPE_CHECKING

from ..effect import effect as eft
from ..status import status as stt
from ..summon import summon as sm
from ..support import support as sp

from ..character.character_skill_enum import CharacterSkill
from ..state.enums import PID
from ..effect.enums import ZONE, TRIGGERING_SIGNAL
from ..effect.structs import StaticTarget

from .enums import PREPROCESSABLES

if TYPE_CHECKING:
    from ..card.card import Card
    from ..state.game_state import GameState

    from .types import Preprocessable


class StatusProcessing:
    @staticmethod
    def loop_one_player_all_statuses(
            game_state: GameState,
            pid: PID,
            f: Callable[[GameState, stt.Status, StaticTarget], GameState]
    ) -> GameState:
        """
        Perform f on all statuses of player pid in order
        f(game_state, status, status_source) -> game_state
        """
        player = game_state.get_player(pid)

        # characters first
        characters = player.get_characters()
        ordered_characters = characters.get_character_in_activity_order()
        for character in ordered_characters:
            # get character's private statuses and add triggerStatusEffect to global effect_stack
            statuses = character.get_all_statuses_ordered_flattened()
            character_id = character.get_id()
            target = StaticTarget(
                pid,
                ZONE.CHARACTERS,
                character_id
            )
            for status in statuses:
                game_state = f(game_state, status, target)

        # combat status
        combat_statuses = player.get_combat_statuses()
        target = StaticTarget(
            pid,
            ZONE.COMBAT_STATUSES,
            -1,  # not used
        )
        for status in combat_statuses:
            game_state = f(game_state, status, target)

        # summons
        summons = player.get_summons()
        target = StaticTarget(
            pid,
            ZONE.SUMMONS,
            -1,
        )
        for summon in summons:
            game_state = f(game_state, summon, target)

        # supports
        supports = player.get_supports()
        for support in supports:
            target = StaticTarget(
                pid,
                ZONE.SUPPORTS,
                support.sid,
            )
            game_state = f(game_state, support, target)

        return game_state

    @staticmethod
    def loop_all_statuses(
            game_state: GameState,
            pid: PID,
            f: Callable[[GameState, stt.Status, StaticTarget], GameState]
    ) -> GameState:
        """
        Perform f on all statuses of player pid and opponent in order
        f(game_state, status, status_source) -> game_state
        """
        game_state = StatusProcessing.loop_one_player_all_statuses(game_state, pid, f)
        game_state = StatusProcessing.loop_one_player_all_statuses(game_state, pid.other(), f)
        return game_state

    @staticmethod
    def trigger_all_statuses_effects(
            game_state: GameState, pid: PID, signal: TRIGGERING_SIGNAL
    ) -> list[eft.Effect]:
        """
        Takes the current game_state, trigger all statuses in order of player pid
        Returns the triggering effects in order (first to last)
        """
        effects: list[eft.Effect] = []

        def f(game_state: GameState, status: stt.Status, target: StaticTarget) -> GameState:
            nonlocal effects
            if isinstance(status, stt.CharacterTalentStatus) \
                    or isinstance(status, stt.EquipmentStatus) \
                    or isinstance(status, stt.CharacterStatus):
                effects.append(eft.TriggerStatusEffect(target, type(status), signal))

            elif isinstance(status, stt.CombatStatus):
                effects.append(eft.TriggerCombatStatusEffect(target.pid, type(status), signal))

            elif isinstance(status, sm.Summon):
                effects.append(eft.TriggerSummonEffect(target.pid, type(status), signal))

            elif isinstance(status, sp.Support):
                effects.append(eft.TriggerSupportEffect(
                    target.pid, type(status), status.sid, signal))

            return game_state

        StatusProcessing.loop_all_statuses(game_state, pid, f)
        return effects

    @staticmethod
    def preprocess_by_all_statuses(
            game_state: GameState,
            pid: PID,
            item: Preprocessable,
            pp_type: PREPROCESSABLES,
    ) -> tuple[GameState, Preprocessable]:
        def f(game_state: GameState, status: stt.Status, status_source: StaticTarget) -> GameState:
            nonlocal item
            item, new_status = status.preprocess(game_state, status_source, item, pp_type)

            if isinstance(status, stt.CharacterTalentStatus) \
                    or isinstance(status, stt.EquipmentStatus) \
                    or isinstance(status, stt.CharacterStatus):
                if new_status is None:
                    game_state = eft.RemoveCharacterStatusEffect(
                        status_source, type(status)).execute(game_state)
                elif new_status != status:
                    assert type(status) == type(new_status)
                    game_state = eft.OverrideCharacterStatusEffect(
                        status_source,
                        new_status,  # type: ignore
                    ).execute(game_state)

            elif isinstance(status, stt.CombatStatus):
                if new_status is None:
                    game_state = eft.RemoveCombatStatusEffect(
                        status_source.pid,
                        type(status),
                    ).execute(game_state)
                elif new_status != status:
                    assert type(status) == type(new_status)
                    game_state = eft.OverrideCombatStatusEffect(
                        status_source.pid,
                        new_status,  # type: ignore
                    ).execute(game_state)

            elif isinstance(status, sm.Summon):
                summon = status
                new_summon = new_status
                pid = status_source.pid
                if new_summon is None:
                    game_state = eft.RemoveSummonEffect(
                        pid,
                        type(summon),
                    ).execute(game_state)
                elif new_summon != summon:
                    assert type(summon) == type(new_summon)
                    game_state = eft.OverrideSummonEffect(
                        pid,
                        new_summon,  # type: ignore
                    ).execute(game_state)

            elif isinstance(status, sp.Support):
                support = status
                new_support = new_status
                pid = status_source.pid
                if new_support is None:
                    game_state = eft.RemoveSupportEffect(
                        pid,
                        support.sid,
                    ).execute(game_state)
                elif new_support != support:
                    assert type(support) == type(new_support)
                    game_state = eft.OverrideSupportEffect(
                        pid,
                        new_support,  # type: ignore
                    ).execute(game_state)

            return game_state

        game_state = StatusProcessing.loop_all_statuses(game_state, pid, f)
        return game_state, item

    @staticmethod
    def inform_all_statuses(
            game_state: GameState,
            pid: PID,
            info: eft.SpecificDamageEffect | CharacterSkill | Card,
            source: None | StaticTarget = None,
    ) -> GameState:
        def f(game_state: GameState, status: stt.Status, status_source: StaticTarget) -> GameState:
            return status.inform(
                game_state,
                status_source,
                info,
                info_source=source,
            )

        game_state = StatusProcessing.loop_all_statuses(game_state, pid, f)
        return game_state
