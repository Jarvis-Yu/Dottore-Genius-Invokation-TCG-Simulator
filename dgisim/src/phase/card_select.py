from typing import Optional
from dgisim.src.state.game import GameState
from dgisim.src.state.player import PlayerState
from dgisim.src.phase.phase import Phase


class CardSelectPhase(Phase):
    def __init__(self) -> None:
        super().__init__()

    def run(self, game_state: GameState) -> GameState:
        p1: PlayerState = game_state.get_player1()
        p2: PlayerState = game_state.get_player2()
        # If both players just entered waiting, make them take actions
        if p1.get_phase() is PlayerState.act.WAIT_PHASE and p2.get_phase() is PlayerState.act.WAIT_PHASE:
            return game_state.factory().player1(  # TODO The chances here can be buffed
                p1.factory().phase(PlayerState.act.ACTION_PHASE).card_redraw_chances(1).build()
            ).player2(
                p2.factory().phase(PlayerState.act.ACTION_PHASE).card_redraw_chances(1).build()
            ).build()
        # Otherwise move to the next game phase
        return game_state.factory().phase(
            game_state.get_mode().starting_hand_select_phase()
        ).build()

    def run_action(self, game_state: GameState, pid: GameState.pid, action) -> GameState:
        # TODO: actually implement something when there is an actually deck
        player: PlayerState = game_state.get_player(pid)
        reducedChances: int = player.get_card_redraw_chances() - 1
        if reducedChances > 0:
            phase: PlayerState.act = player.get_phase()
        else:
            phase: PlayerState.act = PlayerState.act.END_PHASE
        return game_state.factory().player(
            pid,
            player.factory().card_redraw_chances(reducedChances).phase(phase).build()
        ).build()

    def waiting_for(self, game_state: GameState) -> Optional[GameState.pid]:
        players = [game_state.get_player1(), game_state.get_player2()]
        for player in players:
            if player.get_phase() is PlayerState.act.ACTION_PHASE:
                return game_state.get_pid(player)
        return None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CardSelectPhase)

    def __hash__(self) -> int:
        return hash(self.__class__.__name__)
