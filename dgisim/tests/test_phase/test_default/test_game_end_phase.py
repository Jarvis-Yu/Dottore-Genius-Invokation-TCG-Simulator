import unittest

from dgisim.src.phase.default.game_end_phase import GameEndPhase

class TestGameEndPhase(unittest.TestCase):
    def test_eq_and_hash(self):
        phase1 = GameEndPhase()
        phase2 = GameEndPhase()

        self.assertEqual(phase1, phase2)
        self.assertEqual(hash(phase1), hash(phase2))
