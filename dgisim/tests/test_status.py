import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.card.card import *
from dgisim.src.card.cards import Cards
from dgisim.src.dices import ActualDices
from dgisim.src.action.action import *
from dgisim.src.agents import PuppetAgent
from dgisim.src.status.statuses import *
from dgisim.src.status.status import *
from dgisim.src.helper.level_print import GamePrinter
from dgisim.src.helper.quality_of_life import just
from dgisim.tests.helpers.quality_of_life import *


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
            .just_get_character(2)
            .get_character_statuses()
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
            .get_player1() \
            .get_characters() \
            .just_get_character(2)
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
            .get_player1() \
            .get_characters() \
            .just_get_character(2)
        status = character \
            .get_character_statuses() \
            .just_find(MushroomPizzaStatus)
        assert isinstance(status, MushroomPizzaStatus)
        self.assertEqual(character.get_hp(), 3)
        self.assertEqual(status.usages, 1)
