from typing import List

from dgisim.src.player_agent import PlayerAgent
from dgisim.src.state.game_state import GameState
from dgisim.src.action import Action, CardSelectAction, CharacterSelectAction
from dgisim.src.phase.card_select_phase import CardSelectPhase
from dgisim.src.phase.starting_hand_select_phase import StartingHandSelectPhase
from dgisim.src.card.cards import Cards

class NoneAgent(PlayerAgent):
    pass

class BasicAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: List[GameState], pid: GameState.pid) -> Action:
        game_state = history[-1]
        if isinstance(game_state.get_phase(), CardSelectPhase):
            _, selected_cards = game_state.get_player(pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards)
        elif isinstance(game_state.get_phase(), StartingHandSelectPhase):
            return CharacterSelectAction(1)
        return super().choose_action(history, pid)
