"""
Tests the basic weapon cards which's statuses directly use the template of WeaponEquipmentStatus

Cards covered are: MagicGuide, RavenBow, TravelersHandySword, WhiteIronGreatsword, WhiteTassel
"""
import unittest

from .common_imports import *


class TestWeaponEquipmentCard(unittest.TestCase):
    def test_basic_weapons(self):
        base_game = ACTION_TEMPLATE.factory().f_player1(
            lambda p1: p1.factory().f_hand_cards(
                lambda hcs: hcs.add(RavenBow).add(TravelersHandySword)
            ).build()
        ).build()

        # tests that Raven Bow cannot be equiped, but THSword can
        self.assertFalse(RavenBow.loosely_usable(base_game, Pid.P1))
        self.assertTrue(TravelersHandySword.loosely_usable(base_game, Pid.P1))

        game_state = set_active_player_id(base_game, Pid.P1, 3)
        game_state = just(game_state.action_step(Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                dice=ActualDice({Element.OMNI: 2}),
                target=StaticTarget(Pid.P1, Zone.CHARACTERS, 3),
            ),
        )))
        game_state = auto_step(game_state)

        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        p1ac = game_state.player1.just_get_active_character()
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 7)
        self.assertIn(TravelersHandySwordStatus, p1ac.character_statuses)