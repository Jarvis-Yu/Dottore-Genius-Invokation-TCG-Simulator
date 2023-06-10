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

# Empty Agent
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
    def __init__(self, actions: list[PlayerAction] = []) -> None:
        self._actions = actions

    def inject_action(self, action: PlayerAction) -> None:
        self._actions.append(action)

    def choose_action(self, history: List[GameState], pid: GameState.Pid) -> PlayerAction:
        assert self._actions
        return self._actions.pop(0)


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
                    print("DeathSwap")
                    return DeathSwapAction(choice(alive_ids))
                else:
                    raise Exception("Game should end here but not implemented(NOT REACHED)")
                
            # card action
            if selection < 1:
                cards = me.get_hand_cards()
                card: Optional[type[Card]]

                # Consolidation Functions / Helpers
                def try_card_action(card_class, condition, tmp_dices):
                    if cards.contains(card_class) and condition():
                        if active_character is not None:
                            action = CardAction(
                                card_class,
                                CharacterTargetInstruction(
                                    tmp_dices,
                                    StaticTarget(
                                        pid,
                                        Zone.CHARACTER,
                                        active_character.get_id()
                                    )
                                )
                            )
                            if action is None:
                                return None
                            else:
                                print(card_class().name())
                                return action
                        else:
                            print("No Active Character")
                            return None
                        
                
                def dice(element, amount):
                    return available_dices.basically_satisfy(AbstractDices({element: amount}))
                
                # Conditions
                character_injured = lambda: active_character.get_hp() < active_character.get_max_hp()
                missing_energy = lambda: active_character.get_energy() < active_character.get_max_energy()

                # Cards / Conditions / Dices
                cardstuff = [
                    (SweetMadame, character_injured, dice(Element.OMNI, 0)),
                    (MondstadtHashBrown, character_injured, dice(Element.OMNI, 1)),
                    (MushroomPizza, character_injured, dice(Element.OMNI, 1)),
                    (Starsigns, missing_energy, dice(Element.ANY, 2)),
                ]

                for card, condition, dices in cardstuff:
                    action = try_card_action(card, condition, dices)
                    if action is not None:
                        return action

            # normal attack
            if selection < 0.6 and active_character.can_cast_skill():
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 2,
                }))
                if dices is not None:
                    print("NormalAttack")
                    return SkillAction(
                        CharacterSkill.NORMAL_ATTACK,
                        DiceOnlyInstruction(dices),
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
                    print("SWAP")
                    return SwapAction(
                        choice(alive_ids),
                        DiceOnlyInstruction(dices),
                    )
            
            print("EndRound")
            return EndRoundAction()
        
        else:
            raise Exception("No Action Defined")
