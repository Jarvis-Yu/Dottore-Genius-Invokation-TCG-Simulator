
import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.character.character_skill_enum import CharacterSkill
from dgisim.src.card.card import *
from dgisim.src.card.cards import Cards
from dgisim.src.dices import ActualDices
from dgisim.src.action import *
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
            .just_get_character(2)
        status = character \
            .get_character_statuses() \
            .just_find(MushroomPizzaStatus)
        assert isinstance(status, MushroomPizzaStatus)
        self.assertEqual(character.get_hp(), 3)
        self.assertEqual(status.duration, 1)

    def testJueyunGuobaCardTakesEffect(self):
        """
        Pre: active character of both players are "Rhodeia of Loch"
        TODO: move to test_card.py
        """
        base_game_state = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({JueyunGuoba: 1})
            ).build()
        ).build()
        char1 = base_game_state.get_player1().just_get_active_character()
        p1, p2 = PuppetAgent(), PuppetAgent()

        # without JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(SkillAction(
            CharacterSkill.NORMAL_ATTACK,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        hp_without_guoba = gsm.get_game_state().get_player2().just_get_active_character().get_hp()

        # with JueyunGuoba
        gsm = GameStateMachine(base_game_state, p1, p2)
        p1.inject_action(CardAction(
            JueyunGuoba,
            CharacterTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTER,
                    char1.get_id(),
                )
            )
        ))
        p1.inject_action(SkillAction(
            CharacterSkill.NORMAL_ATTACK,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            hp_without_guoba - 1
        )
        self.assertFalse(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba on other character
        gsm = GameStateMachine(base_game_state, p1, p2)
        guobaed_char_id = char1.get_id() % 3 + 1  # next character
        p1.inject_action(CardAction(
            JueyunGuoba,
            CharacterTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTER,
                    guobaed_char_id,
                )
            )
        ))
        p1.inject_action(SkillAction(
            CharacterSkill.NORMAL_ATTACK,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.one_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .get_characters()
            .just_get_character(guobaed_char_id)
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )
        gsm.one_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            hp_without_guoba
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .get_characters()
            .just_get_character(guobaed_char_id)
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )

        # with JueyunGuoba but cast elemental skill
        game_state = set_active_player_id(base_game_state, GameState.Pid.P1, 2)
        gsm = GameStateMachine(game_state, p1, p2)
        p1.inject_action(CardAction(
            JueyunGuoba,
            CharacterTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    GameState.Pid.P1,
                    Zone.CHARACTER,
                    2,
                )
            )
        ))
        p1.inject_action(SkillAction(
            CharacterSkill.ELEMENTAL_SKILL1,
            DiceOnlyInstruction(dices=ActualDices({})),
        ))
        gsm.player_step()  # p1 has JueyunGuoba
        gsm.auto_step()
        gsm.player_step()  # p1 normal attacks
        gsm.auto_step()  # process normal attack
        self.assertEqual(
            gsm.get_game_state().get_player2().just_get_active_character().get_hp(),
            7,
        )
        self.assertTrue(
            gsm
            .get_game_state()
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(JueyunGuobaStatus)
        )
