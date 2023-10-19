import unittest

from src.dgisim.status.status import *
from src.dgisim.status.statuses import *

class TestStatuses(unittest.TestCase):
    pass

class TestEquipmentStatuses(unittest.TestCase):
    def test_replacing_same_category(self):
        equipments = EquipmentStatuses(())
        equipments = equipments.update_status(RavenBowStatus())
        self.assertIn(RavenBowStatus, equipments)
        equipments = equipments.update_status(GamblersEarringsStatus())
        equipments = equipments.update_status(TravelersHandySwordStatus())
        self.assertNotIn(RavenBowStatus, equipments)
        self.assertIn(TravelersHandySwordStatus, equipments)
