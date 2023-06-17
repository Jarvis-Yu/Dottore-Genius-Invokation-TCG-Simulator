
import unittest

from dgisim.tests.helpers.game_state_templates import *
from dgisim.tests.helpers.quality_of_life import *
from dgisim.src.game_state_machine import GameStateMachine
from dgisim.src.agents import PuppetAgent
from dgisim.src.action import *
from dgisim.src.character.character import *
from dgisim.src.card.card import *
from dgisim.src.status.status import *
from dgisim.src.summon.summon import *

class TestKaeya(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(1).build()  # make active character Rhodeia
        ).f_hand_cards(
            lambda hcs: hcs.add(ColdBloodedStrike)  # TODO: replace with Rhodeia Talent Card
        ).build()
    ).f_player2(
        lambda p: p.factory().phase(PlayerState.Act.END_PHASE).build()
    ).build()
    assert type(BASE_GAME.get_player1().just_get_active_character()) is RhodeiaOfLoch

    def test_frog(self):
        a1, a2 = PuppetAgent(), PuppetAgent()
        base_game = self.BASE_GAME.factory().f_player2(
            lambda p: p.factory().f_summons(
                lambda ss: ss.update_summon(OceanicMimicFrogSummon())
            ).build()
        ).build()

        # first hit
        game_state = add_damage_effect(base_game, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 9)
        self.assertEqual(frog.usages, 1)

        # second hit
        game_state = add_damage_effect(game_state, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 8)
        self.assertEqual(frog.usages, 0)

        # third hit
        game_state = add_damage_effect(game_state, 2, Element.PHYSICAL)
        game_state = auto_step(game_state)
        ac = game_state.get_player2().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 6)
        self.assertEqual(frog.usages, 0)

        # end round and frog attacks & disappears
        gsm = GameStateMachine(game_state, a1, a2)
        a1.inject_action(EndRoundAction())
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        ac = game_state.get_player1().just_get_active_character()
        optional_frog = game_state.get_player2().get_summons().find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 8)
        self.assertTrue(ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertTrue(optional_frog is None)

        # end round with frog(2) keeps frog untouched
        gsm = GameStateMachine(base_game, a1, a2)
        a1.inject_action(EndRoundAction())
        gsm.player_step()
        gsm.auto_step()
        game_state = gsm.get_game_state()
        ac = game_state.get_player1().just_get_active_character()
        frog = game_state.get_player2().get_summons().just_find(OceanicMimicFrogSummon)
        self.assertEqual(ac.get_hp(), 10)
        self.assertFalse(ac.get_elemental_aura().contains(Element.HYDRO))
        self.assertTrue(frog.usages, 2)
