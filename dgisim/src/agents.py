from typing import List, Optional
from random import random, choice
from dgisim.src.action import PlayerAction

from dgisim.src.player_agent import PlayerAgent
from dgisim.src.state.game_state import GameState
from dgisim.src.action import *
from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.phase.roll_phase import RollPhase
from dgisim.src.phase.action_phase import ActionPhase
from dgisim.src.card.cards import Cards
from dgisim.src.character.character import CharacterSkill
from dgisim.src.dices import AbstractDices, ActualDices
from dgisim.src.element.element import Element
from dgisim.src.card.card import *


class NoneAgent(PlayerAgent):
    pass


class LazyAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards)
        
        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(1)
        
        elif isinstance(curr_phase, RollPhase):
            raise Exception("No Action Defined")
        
        elif isinstance(curr_phase, ActionPhase):
            return EndRoundAction()
        
        else:
            raise Exception("No Action Defined")


class PuppetAgent(PlayerAgent):
    def __init__(self, actions: Optional[list[PlayerAction]] = None) -> None:
        if actions is None:
            self._actions = []
        else:
            self._actions = actions

    def inject_action(self, action: PlayerAction) -> None:
        self._actions.append(action)

    def inject_actions(self, actions: list[PlayerAction]) -> None:
        self._actions += actions

    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        assert self._actions
        return self._actions.pop(0)

    def clear(self) -> None:
        self._actions = []

    def __str__(self) -> str:
        return f"PuppetAgent[{', '.join(str(action) for action in self._actions)}]"


class HardCodedRandomAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards)
        
        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(1)
        
        elif isinstance(curr_phase, RollPhase):
            raise Exception("No Action Defined")
        
        elif isinstance(curr_phase, ActionPhase):
            selection = random()
            me = game_state.get_player(pid)
            available_dices = me.get_dices()
            active_character = me.get_active_character()

            assert active_character is not None

            # death swap
            if active_character.defeated():
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if alive_ids:
                    return DeathSwapAction(choice(alive_ids))
                else:
                    raise Exception("Game should end here but not implemented(NOT REACHED)")
                
            # food card
            character_injured = active_character.get_hp() < active_character.get_max_hp()
            if selection < 1:
                cards = me.get_hand_cards()
                card: Optional[type[Card]]
                tmp_dices = ActualDices({})

                if cards.contains(SweetMadame) and character_injured:
                    card = SweetMadame
                    tmp_dices = ActualDices({Element.OMNI: 0})
                elif cards.contains(MondstadtHashBrown) and character_injured:
                    tmp_dices = ActualDices({Element.OMNI: 1})
                    card = MondstadtHashBrown
                elif cards.contains(MushroomPizza) and character_injured:
                    tmp_dices = ActualDices({Element.OMNI: 1})
                    card = MushroomPizza
                else:
                    card = None
                
                if card is not None and not active_character.satiated():
                    return CardAction(
                        card,
                        CharacterTargetInstruction(
                            dices=tmp_dices,
                            target=StaticTarget(
                                pid,
                                Zone.CHARACTER,
                                active_character.get_id(),
                            )
                        )
                    )
                
            # starsigns
            if cards.contains(Starsigns):
                if active_character.get_energy() < active_character.get_max_energy():
                    card = Starsigns
                    tmp_dices = ActualDices({Element.ANY: 2})
                    return CardAction(
                        card,
                        CharacterTargetInstruction(
                            dices=tmp_dices,
                            target=StaticTarget(
                                pid,
                                Zone.CHARACTER,
                                active_character.get_id(),
                            )
                        )
                    )

            # elemental skill1
            if selection < 0.5 and active_character.can_cast_skill():
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 2,
                }))
                if dices is not None:
                    return SkillAction(
                        CharacterSkill.ELEMENTAL_SKILL1,
                        DiceOnlyInstruction(dices=dices),
                    )

            # normal attack
            if selection < 0.5 and active_character.can_cast_skill():
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 2,
                }))
                if dices is not None:
                    return SkillAction(
                        CharacterSkill.NORMAL_ATTACK,
                        DiceOnlyInstruction(dices=dices),
                    )
            
            # swap character
            if selection < 0.7:
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 1,
                }))
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if dices is not None and alive_ids:
                    return SwapAction(
                        choice(alive_ids),
                        DiceOnlyInstruction(dices=dices),
                    )
            
            return EndRoundAction()
        
        else:
            raise Exception("No Action Defined")
