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
            reward_method: Callable[[GameState], int | float] = real_reward,
            invalid_action_penalty: int | float = -0.1,
    ):
        """
        :param mode: the mode of the game.
        :param encoding_plan: the encoding plan of the game.
        :param reward_method: the reward method of the game.
        :param invalid_action_penalty: the penalty for invalid action.
        """
        self._mode = mode
        self._encoding_plan = encoding_plan
        self._reward_method = reward_method
        self._invalid_action_penalty = invalid_action_penalty
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

    def reset_with_decks(self, deck1: Deck, deck2: Deck) -> None:
        """
        Resets the game state with the given decks.
        """
        self._last_deck1 = deck1
        self._last_deck2 = deck2
        self._last_reset = self._reset_with_decks
        self.reset()

    def _reset_with_decks(self) -> None:
        assert self._last_deck1 is not None
        assert self._last_deck2 is not None
        self._curr_state = GameState.from_decks(self._mode, self._last_deck1, self._last_deck2)

    def full_view(self) -> GameState:
        """
        :returns: the game state without any perspective (all cards & dice visible).
        """
        return self._curr_state

    def view(self) -> tuple[GameState, list[int], int | float, int, bool]:
        """
        :returns: game state, encoded state, reward, turn, done

        The game state is in the perspective view of the current player.

        The `turn` indicates the player that should take action next.
        """
        match self._curr_state.waiting_for():
            case Pid.P1:
                turn = 1
                perspective_state = self._curr_state.prespective_view(Pid.P1)
            case _:
                turn = 2
                perspective_state = self._curr_state.prespective_view(Pid.P2)
        return (
            perspective_state,
            perspective_state.encoding(self._encoding_plan),
            0,
            turn,
            self._curr_state.game_end(),
        )

    def step(
            self,
            action: list[int] | PlayerAction
    ) -> tuple[GameState, list[int], int | float, int, bool]:
        """
        :param action: the action to take.
                       It can either be a list of int as the encoded action,
                       or a PlayerAction object.

        :returns: game state, encoded state, reward, turn, done

        The `game state` is in the perspective view of the current player.

        The `turn` indicates the player that should take action next.

        An invalid action will result-in the same state with a penalty.
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
                perspective_state = self._curr_state.prespective_view(
                    Pid.P1 if turn == 1 else Pid.P2
                )
                return (
                    perspective_state,
                    perspective_state.encoding(self._encoding_plan),
                    (
                        self._invalid_action_penalty
                        if turn == 1
                        else -self._invalid_action_penalty
                    ),  # penalty for invalid action
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
            perspective_state = self._curr_state.prespective_view(Pid.P1 if turn == 1 else Pid.P2)
            return (
                perspective_state,
                perspective_state.encoding(self._encoding_plan),
                (
                    self._invalid_action_penalty
                    if turn == 1
                    else -self._invalid_action_penalty
                ),  # penalty for invalid action
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
                perspective_state = self._curr_state
            case Pid.P1:
                turn = 1
                perspective_state = self._curr_state.prespective_view(Pid.P1)
            case _:
                turn = 2
                perspective_state = self._curr_state.prespective_view(Pid.P2)

        return (
            perspective_state,
            perspective_state.encoding(encoding_plan),
            self._reward_method(self._curr_state),
            turn,
            self._curr_state.game_end(),
        )
