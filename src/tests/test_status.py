import unittest

from src.dgisim.action.action import *
from src.dgisim.agents import PuppetAgent
from src.dgisim.card.card import *
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.status.status import *
from src.dgisim.status.statuses import *
from src.tests.helpers.game_state_templates import *
from src.tests.helpers.quality_of_life import *


class TestStatus(unittest.TestCase):

    def testSatiatedStatusRemovedDuringEndRound(self):
        game_state = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().character_statuses(
                        Statuses((SatiatedStatus(), ))
                    ).build()
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
        gsm.step_until_next_phase()
        self.assertFalse(
            gsm
            .get_game_state()
            .player1
            .characters
            .just_get_character(2)
            .character_statuses
            .contains(SatiatedStatus)
        )

    def testMushroomPizzaStatusRemovedDuringEndRound(self):
        game_state = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().character_statuses(
                        Statuses((MushroomPizzaStatus(usages=1), ))
                    ).hp(
                        2
                    ).build()
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
        gsm.step_until_next_phase()
        character = gsm \
            .get_game_state() \
            .player1 \
            .characters \
            .just_get_character(2)
        self.assertEqual(character.hp, 3)
        self.assertFalse(
            character
            .character_statuses
            .contains(MushroomPizzaStatus)
        )

    def testMushroomPizzaStatusDurationDecreaseDuringEndRound(self):
        game_state = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().character_statuses(
                        Statuses((MushroomPizzaStatus(usages=2), ))
                    ).hp(
                        2
                    ).build()
                ).build()
            ).build()
        ).build()
        gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
        gsm.step_until_next_phase()
        character = gsm \
            .get_game_state() \
            .player1 \
            .characters \
            .just_get_character(2)
        status = character \
            .character_statuses \
            .just_find(MushroomPizzaStatus)
        assert isinstance(status, MushroomPizzaStatus)
        self.assertEqual(character.hp, 3)
        self.assertEqual(status.usages, 1)
