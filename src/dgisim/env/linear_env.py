from typing import Callable, Literal

from ..action.action import PlayerAction
from ..deck import Deck
from ..encoding.encoding_plan import EncodingPlan, encoding_plan
from ..mode import DefaultMode, Mode
from ..state.enums import Pid
from ..state.game_state import GameState

__all__ = ["LinearEnv"]

def real_reward(state: GameState) -> int:
    if not state.game_end():
        return 0
    elif state.get_winner() is Pid.P1:
        return 1
    elif state.get_winner() is Pid.P2:
        return -1
    else:
        assert state.get_winner() is None
        return 0

class LinearEnv:
    def __init__(
            self,
            mode: Mode = DefaultMode(),
            encoding_plan: EncodingPlan = encoding_plan,
            reward_method: Callable[[GameState], int] = real_reward,
    ):
        self._mode = mode
        self._encoding_plan = encoding_plan
        self._reward_method = reward_method
        self._last_deck1: None | Deck = None
        self._last_deck2: None | Deck = None
        self._curr_state: GameState
        self._last_reset: Callable[[], None] = self._reset_random
        self.reset()

    def reset(self) -> None:
        """
        Repeats the last reset method.
        """
        self._last_reset()
        while self._curr_state.waiting_for() is None and not self._curr_state.game_end():
            self._curr_state = self._curr_state.step()

    def reset_random(self) -> None:
        """
        Resets the game state by with random decks under the mode.
        """
        self._last_reset = self._reset_random
        self.reset()

    def _reset_random(self) -> None:
        self._curr_state = GameState.from_default(self._mode)

    def reset_by_decks(self, deck1: Deck, deck2: Deck) -> None:
        """
        Resets the game state by the given decks.
        """
        self._last_deck1 = deck1
        self._last_deck2 = deck2
        self._last_reset = self._reset_by_decks
        self.reset()

    def _reset_by_decks(self) -> None:
        assert self._last_deck1 is not None
        assert self._last_deck2 is not None
        self._curr_state = GameState.from_decks(self._mode, self._last_deck1, self._last_deck2)

    def view(self) -> tuple[GameState, list[int], int | float, int, bool]:
        """
        :returns: game state, encoded state, reward, turn, done
        """
        match self._curr_state.waiting_for():
            case Pid.P1:
                turn = 1
            case _:
                turn = 2
        return (
            self._curr_state,
            self._curr_state.encoding(self._encoding_plan),
            0,
            turn,
            self._curr_state.game_end(),
        )

    def step(
            self,
            action: list[int] | PlayerAction
    ) -> tuple[GameState, list[int], int | float, int, bool]:
        """
        :returns: game state, encoded state, reward, turn, done
        """
        assert not self._curr_state.game_end()

        match self._curr_state.waiting_for():
            case Pid.P1:
                turn = 1
            case _:
                turn = 2

        # decode action if necessary
        if isinstance(action, list):
            optional_action = PlayerAction.decoding(action, self._encoding_plan)
            if optional_action is None:
                return (
                    self._curr_state,
                    self._curr_state.encoding(self._encoding_plan),
                    -1 if turn == 1 else 1,  # penalty for invalid action
                    turn,
                    self._curr_state.game_end(),
                )
            action = optional_action
        assert isinstance(action, PlayerAction)

        curr_player = self._curr_state.waiting_for()
        assert curr_player is not None
        try:
            state = self._curr_state.action_step(curr_player, action)
        except Exception as e:
            return (
                self._curr_state,
                self._curr_state.encoding(self._encoding_plan),
                -1 if turn == 1 else 1,  # penalty for invalid action
                turn,
                self._curr_state.game_end(),
            )
        assert state is not None
        while state.waiting_for() is None and not state.game_end():
            state = state.step()
        self._curr_state = state

        match self._curr_state.waiting_for():
            case None:
                turn = 0
            case Pid.P1:
                turn = 1
            case _:
                turn = 2

        return (
            self._curr_state,
            self._curr_state.encoding(encoding_plan),
            self._reward_method(self._curr_state),
            turn,
            self._curr_state.game_end(),
        )
