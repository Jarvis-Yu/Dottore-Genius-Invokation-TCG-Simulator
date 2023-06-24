from __future__ import annotations
from typing import Callable

import dgisim.src.state.game_state as gs
import dgisim.src.status.status as stt
import dgisim.src.effect.effect as eft
import dgisim.src.summon.summon as sm
import dgisim.src.card.card as cd
from dgisim.src.character.character_skill_enum import CharacterSkill


class StatusProcessing:
    @staticmethod
    def loop_one_player_all_statuses(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            f: Callable[[gs.GameState, stt.Status, eft.StaticTarget], gs.GameState]
    ) -> gs.GameState:
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
            target = eft.StaticTarget(
                pid,
                eft.Zone.CHARACTER,
                character_id
            )
            for status in statuses:
                game_state = f(game_state, status, target)

        # combat status
        combat_statuses = player.get_combat_statuses()
        target = eft.StaticTarget(
            pid,
            eft.Zone.COMBAT_STATUSES,
            -1,  # not used
        )
        for status in combat_statuses:
            game_state = f(game_state, status, target)

        # summons
        summons = player.get_summons()
        target = eft.StaticTarget(
            pid,
            eft.Zone.SUMMONS,
            -1
        )
        for summon in summons:
            game_state = f(game_state, summon, target)

        # supports TODO

        return game_state

    @staticmethod
    def loop_all_statuses(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            f: Callable[[gs.GameState, stt.Status, eft.StaticTarget], gs.GameState]
    ) -> gs.GameState:
        """
        Perform f on all statuses of player pid and opponent in order
        f(game_state, status, status_source) -> game_state
        """
        game_state = StatusProcessing.loop_one_player_all_statuses(game_state, pid, f)
        game_state = StatusProcessing.loop_one_player_all_statuses(game_state, pid.other(), f)
        return game_state

    @staticmethod
    def trigger_all_statuses_effects(
            game_state: gs.GameState, pid: gs.GameState.Pid, signal: eft.TriggeringSignal
    ) -> list[eft.Effect]:
        """
        Takes the current game_state, trigger all statuses in order of player pid
        Returns the triggering effects in order (first to last)
        """
        effects: list[eft.Effect] = []

        def f(game_state: gs.GameState, status: stt.Status, target: eft.StaticTarget) -> gs.GameState:
            nonlocal effects
            if isinstance(status, stt.CharacterTalentStatus) \
                    or isinstance(status, stt.EquipmentStatus) \
                    or isinstance(status, stt.CharacterStatus):
                effects.append(eft.TriggerStatusEffect(target, type(status), signal))

            elif isinstance(status, stt.CombatStatus):
                effects.append(eft.TriggerCombatStatusEffect(target.pid, type(status), signal))

            elif isinstance(status, sm.Summon):
                effects.append(eft.TriggerSummonEffect(target.pid, type(status), signal))

            return game_state

        StatusProcessing.loop_all_statuses(game_state, pid, f)
        return effects

    @staticmethod
    def preprocess_by_all_statuses(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            item: eft.Preprocessable,
            pp_type: stt.Status.PPType,
    ) -> tuple[gs.GameState, eft.Preprocessable]:
        def f(game_state: gs.GameState, status: stt.Status, status_source: eft.StaticTarget) -> gs.GameState:
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

            return game_state

        game_state = StatusProcessing.loop_all_statuses(game_state, pid, f)
        return game_state, item

    @staticmethod
    def inform_all_statuses(
            game_state: gs.GameState,
            pid: gs.GameState.Pid,
            info: eft.SpecificDamageEffect | CharacterSkill | cd.Card,
            source: None | eft.StaticTarget = None,
    ) -> gs.GameState:
        def f(game_state: gs.GameState, status: stt.Status, status_source: eft.StaticTarget) -> gs.GameState:
            return status.inform(
                game_state,
                status_source,
                info,
                info_source=source,
            )

        game_state = StatusProcessing.loop_all_statuses(game_state, pid, f)
        return game_state
