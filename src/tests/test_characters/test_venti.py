import unittest

from src.tests.test_characters.common_imports import *


class TestVenti(unittest.TestCase):
    BASE_GAME = ACTION_TEMPLATE.factory().f_player1(
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                2
            ).character(
                Venti.from_default(2)
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(EmbraceOfWinds)
        ).build()
    ).build()
    assert type(BASE_GAME.player1.just_get_active_character()) is Venti

    def test_normal_attack(self):
        game_state = step_skill(
            self.BASE_GAME,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 3}),
        )
        p2ac = game_state.player2.just_get_active_character()
        self.assertEqual(p2ac.hp, 8)
        self.assertFalse(p2ac.elemental_aura.has_aura())

    def test_elemental_skill1(self):
        game_state = oppo_aura_elem(self.BASE_GAME, Element.HYDRO)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.SKILL2,
            dice=ActualDice({Element.OMNI: 3}),
        )
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        self.assertEqual(p2cs.just_get_character(1).hp, 8)
        self.assertEqual(p2cs.just_get_character(2).hp, 9)
        self.assertEqual(p2cs.just_get_character(3).hp, 9)
        self.assertNotIn(Element.HYDRO, p2cs.just_get_character(1).elemental_aura)
        self.assertIn(Element.HYDRO, p2cs.just_get_character(2).elemental_aura)
        self.assertIn(Element.HYDRO, p2cs.just_get_character(3).elemental_aura)
        self.assertIn(StormzoneStatus, p1.combat_statuses)
        self.assertEqual(p1.combat_statuses.just_find(StormzoneStatus).usages, 2)

    def test_elemental_burst(self):
        game_state = fill_energy_for_all(self.BASE_GAME)
        game_state = oppo_aura_elem(game_state, Element.CRYO)
        game_state = step_skill(
            game_state,
            Pid.P1,
            CharacterSkill.ELEMENTAL_BURST,
            ActualDice({Element.OMNI: 3}),
        )
        p1 = game_state.player1
        p2cs = game_state.player2.characters
        self.assertEqual(p2cs.just_get_character(1).hp, 8)
        self.assertEqual(p2cs.just_get_character(2).hp, 9)
        self.assertEqual(p2cs.just_get_character(3).hp, 9)
        self.assertNotIn(Element.CRYO, p2cs.just_get_character(1).elemental_aura)
        self.assertIn(Element.CRYO, p2cs.just_get_character(2).elemental_aura)
        self.assertIn(Element.CRYO, p2cs.just_get_character(3).elemental_aura)
        self.assertIn(StormEyeSummon, p1.summons)
        self.assertEqual(p1.summons.just_find(StormEyeSummon).usages, 2)

    def test_stormzone_status(self):
        base_state = AddCombatStatusEffect(Pid.P1, StormzoneStatus).execute(self.BASE_GAME)
        # try swaps, if no exception then considered passed
        game_state = step_swap(base_state, Pid.P1, 1, cost=0)
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, 3, cost=0)
        game_state = step_swap(game_state, Pid.P1, 2, cost=1)
        p1 = game_state.player1
        self.assertNotIn(StormzoneStatus, p1.combat_statuses)

    def test_storm_eye_summon(self):
        # starting with self2 oppo1 drags to oppo2
        base_state = AddSummonEffect(Pid.P1, StormEyeSummon).execute(self.BASE_GAME)
        game_state = next_round(base_state)
        p2cs = game_state.player2.characters
        p2ac = p2cs.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(1).hp, 8)
        self.assertEqual(p2ac.id, 2)

        # starting with self2 oppo3 drags to oppo2
        base_state = AddSummonEffect(Pid.P1, StormEyeSummon).execute(self.BASE_GAME)
        game_state = step_action(base_state, Pid.P1, EndRoundAction())
        game_state = step_swap(game_state, Pid.P2, 3)
        game_state = next_round(game_state)
        p2cs = game_state.player2.characters
        p2ac = p2cs.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(3).hp, 8)
        self.assertEqual(p2ac.id, 2)

        # starting with self2 oppo2 doesn't swap
        base_state = AddSummonEffect(Pid.P1, StormEyeSummon).execute(self.BASE_GAME)
        game_state = step_action(base_state, Pid.P1, EndRoundAction())
        game_state = step_swap(game_state, Pid.P2, 2)
        game_state = next_round(game_state)
        p2cs = game_state.player2.characters
        p2ac = p2cs.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(2).hp, 8)
        self.assertEqual(p2ac.id, 2)

        # starting with self2 oppo1 with oppo2 dead swaps to oppo3
        base_state = AddSummonEffect(Pid.P1, StormEyeSummon).execute(self.BASE_GAME)
        base_state = kill_character(base_state, 2, hp=1)
        game_state = step_skill(base_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_swap(game_state, Pid.P2, 2)
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P2, DeathSwapAction(char_id=1))
        game_state = next_round(game_state)
        p2cs = game_state.player2.characters
        p2ac = p2cs.just_get_active_character()
        self.assertEqual(p2cs.just_get_character(1).hp, 6)
        self.assertEqual(p2ac.id, 3)

    def test_talent_card(self):
        game_state = step_action(self.BASE_GAME, Pid.P1, CardAction(
            card=EmbraceOfWinds,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.ANEMO: 3}))
        ))
        game_state = step_action(game_state, Pid.P2, EndRoundAction())
        game_state = step_swap(game_state, Pid.P1, char_id=1, cost=0)
        self.assertIn(WindsOfHarmonyStatus, game_state.player1.combat_statuses)

    def test_winds_of_harmony_status(self):
        base_state = AddCombatStatusEffect(Pid.P1, WindsOfHarmonyStatus).execute(self.BASE_GAME)
        
        # normal attacks gets correctly reduced cost
        self.assertRaises(Exception, lambda: step_skill(
            base_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.GEO: 2}),
        ))
        game_state = step_skill(
            base_state,
            Pid.P1,
            CharacterSkill.SKILL1,
            dice=ActualDice({Element.OMNI: 1, Element.GEO: 1}),
        )
        self.assertNotIn(WindsOfHarmonyStatus, game_state.player1.combat_statuses)

        # disappears next round
        game_state = next_round(base_state)
        self.assertNotIn(WindsOfHarmonyStatus, game_state.player1.combat_statuses)
