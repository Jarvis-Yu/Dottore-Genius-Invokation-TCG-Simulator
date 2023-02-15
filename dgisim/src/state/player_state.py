class PlayerState:
  ACTION_PHASE = "Action Phase"
  WAIT_PHASE = "Wait Phase"
  END_PHASE = "End Phase"

  def __init__(self):
    self._phase = self.ACTION_PHASE
    self._chars = None
    self._active_char = None
    self._dices = None
    self._deck = None
    self._hand = None
    self._supports = None
    self._summons = None
    self._moves = 0

  def isEndPhase(self):
    return True
    return self._phase is self.END_PHASE

  @staticmethod
  def examplePlayer():
    return PlayerState()