import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.card.cards import *
from dgisim.src.card.card import *
from dgisim.src.status.status import *
from dgisim.src.support.support import *
from dgisim.src.agents import *
from dgisim.src.state.enums import PID


class TestNorthernSmokedChicken(unittest.TestCase):
    def test_northern_smoked_chicken(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p: p.factory().hand_cards(
                Cards({NorthernSmokedChicken: 2})
            ).build()
        ).build()

        # test giving wrong num of dices
        card_action = CardAction(
            card=NorthernSmokedChicken,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 1})),
        )
        self.assertRaises(
            Exception,
            lambda: base_game.action_step(PID.P1, card_action)
        )

        # test giving right num of dices
        card_action = CardAction(
            card=NorthernSmokedChicken,
            instruction=StaticTargetInstruction(
                dices=ActualDices({}),
                target=StaticTarget(
                    pid=PID.P1,
                    zone=Zone.CHARACTERS,
                    id=1,
                )
            ),
        )
        game_state = base_game.action_step(PID.P1, card_action)
        assert game_state is not None
        buffed_game_state = auto_step(game_state)

        self.assertEqual(
            buffed_game_state
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .just_find(NorthernSmokedChickenStatus)
            .usages,
            1
        )
        self.assertTrue(
            buffed_game_state.get_player1().just_get_active_character().get_character_statuses()
            .contains(SatiatedStatus)
        )

        # test normal attack with 3 dices fails
        normal_attack_action = SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 3}))
        )
        self.assertRaises(
            Exception,
            lambda: buffed_game_state.action_step(PID.P1, normal_attack_action)
        )

        # test normal attack with 2 dices pass
        normal_attack_action = SkillAction(
            skill=CharacterSkill.NORMAL_ATTACK,
            instruction=DiceOnlyInstruction(dices=ActualDices({Element.OMNI: 2}))
        )
        game_state = buffed_game_state.action_step(PID.P1, normal_attack_action)
        assert game_state is not None
        game_state = auto_step(game_state)

        self.assertFalse(
            game_state
            .get_player1()
            .just_get_active_character()
            .get_character_statuses()
            .contains(NorthernSmokedChickenStatus)
        )

        # test teammate cannot use this
        game_state = buffed_game_state.factory().f_player1(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().active_character_id(2).build()
            ).build()
        ).build()
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(PID.P1, normal_attack_action)  # type: ignore
        )

        # test opponent cannot use this
        game_state = buffed_game_state.action_step(PID.P1, EndRoundAction())
        assert game_state is not None
        game_state = auto_step(game_state)
        self.assertRaises(
            Exception,
            lambda: game_state.action_step(PID.P2, normal_attack_action)
        )
