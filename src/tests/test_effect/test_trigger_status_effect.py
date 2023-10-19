import unittest

from src.dgisim.effect.effect import *
from src.dgisim.effect.structs import StaticTarget
from src.dgisim.effect.enums import Zone, TriggeringSignal
from src.dgisim.status.status import *
from src.dgisim.summon.summon import *
from src.dgisim.support.support import *
from src.tests.helpers.game_state_templates import *

class TestTriggerStatusEffect(unittest.TestCase):
    def test_execute_fail(self):
        self.assertIs(
            TriggerStatusEffect(
                StaticTarget(Pid.P1, Zone.CHARACTERS, 1),
                status=HiddenStatus,
                signal=TriggeringSignal.COMBAT_ACTION,
            ).execute(ACTION_TEMPLATE),
            ACTION_TEMPLATE
        )

        self.assertIs(
            TriggerCombatStatusEffect(
                Pid.P1,
                status=CombatStatus,
                signal=TriggeringSignal.COMBAT_ACTION,
            ).execute(ACTION_TEMPLATE),
            ACTION_TEMPLATE
        )

        self.assertIs(
            TriggerSummonEffect(
                Pid.P1,
                summon=Summon,
                signal=TriggeringSignal.COMBAT_ACTION,
            ).execute(ACTION_TEMPLATE),
            ACTION_TEMPLATE
        )

        self.assertIs(
            TriggerSupportEffect(
                Pid.P1,
                support_type=Support,
                sid=1,
                signal=TriggeringSignal.COMBAT_ACTION,
            ).execute(ACTION_TEMPLATE),
            ACTION_TEMPLATE
        )
