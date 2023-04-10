from typing import List, Optional
from random import random, choice

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
            # food card
            character_injured = active_character.get_hp() < active_character.get_max_hp()
            if selection < 1:
                cards = me.get_hand_cards()
                card: Optional[type[Card]]
                if cards.contains(SweetMadame):
                    print(f"{pid} has SweetMadame")
                else:
                    print(f"{pid} doesn't have SweetMadame")
                if cards.contains(SweetMadame) and character_injured:
                    card = SweetMadame
                # elif cards.contains_type(MondstadtHashBrown) and character_injured:
                #     card = MondstadtHashBrown
                else:
                    card = None
                if card is not None and not active_character.stuffed():
                    tmp_dices = ActualDices({})
                    print(card().name())
                    return CardAction(
                        card,
                        CharacterTargetInstruction(
                            tmp_dices,
                            StaticTarget(
                                pid,
                                Zone.CHARACTER,
                                active_character.get_id(),
                            )
                        )
                    )
            # normal attack
            if selection < 0.6:
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
