import unittest

from dgisim.src.effect.effect import *
from dgisim.src.effect.structs import StaticTarget
from dgisim.src.effect.enums import Zone, TriggeringSignal
from dgisim.src.status.status import *
from dgisim.src.summon.summon import *
from dgisim.src.support.support import *
from dgisim.tests.helpers.game_state_templates import *

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
