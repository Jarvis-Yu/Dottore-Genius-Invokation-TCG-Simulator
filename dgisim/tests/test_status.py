
import unittest

from dgisim.tests.game_state_templates import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.agents import PuppetAgent
from dgisim.src.status.statuses import *
from dgisim.src.status.status import *


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
            .get_player1()
            .get_characters()
            .get_just_character(2)
            .get_character_statuses()
            .contains(SatiatedStatus)
        )

    def testMushroomPizzaStatusRemovedDuringEndRound(self):
        game_state = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().character_statuses(
                        Statuses((MushroomPizzaStatus(duration=1), ))
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
            .get_player1() \
            .get_characters() \
            .get_just_character(2)
        self.assertEqual(character.get_hp(), 3)
        self.assertFalse(
            character
            .get_character_statuses()
            .contains(MushroomPizzaStatus)
        )

    def testMushroomPizzaStatusDurationDecreaseDuringEndRound(self):
        game_state = END_TEMPLATE.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    2,
                    lambda c: c.factory().character_statuses(
                        Statuses((MushroomPizzaStatus(duration=2), ))
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
            .get_player1() \
            .get_characters() \
            .get_just_character(2)
        status = character \
            .get_character_statuses() \
            .just_find(MushroomPizzaStatus)
        assert isinstance(status, MushroomPizzaStatus)
        self.assertEqual(character.get_hp(), 3)
        self.assertEqual(status.duration, 1)
