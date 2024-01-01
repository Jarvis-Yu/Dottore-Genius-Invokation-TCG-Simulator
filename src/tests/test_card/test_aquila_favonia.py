import unittest

from .common_imports import *

class TestAquilaFavonia(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        for i in range(3):
            base_state = PublicAddCardEffect(Pid.P1, AquilaFavonia).execute(base_state)
        base_state = replace_character(base_state, Pid.P1, Keqing, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Jean, char_id=1)
        base_state = replace_character(base_state, Pid.P1, Bennett, char_id=1)
        base_state = replace_character(base_state, Pid.P2, Keqing, char_id=1)
        base_state = grant_all_thick_shield(base_state)
        base_state = add_dmg_listener(base_state, Pid.P1)
        for i in range(1, 4):
            base_state = simulate_status_dmg(base_state, 5, pid=Pid.P1, char_id=i)

        # equip for all
        game_state = base_state
        for i in range(1, 4):
            game_state = step_action(game_state, Pid.P1, CardAction(
                card=AquilaFavonia,
                instruction=StaticTargetInstruction(
                    dice=ActualDice({Element.PYRO: 3}),
                    target=StaticTarget.from_char_id(Pid.P1, i),
                )
            ))

        # test passive only affect active char (and usages == 2)
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 6)
        self.assertEqual(p1c2.hp, 5)
        self.assertEqual(p1c3.hp, 5)
        
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 5)
        self.assertEqual(p1c3.hp, 5)

        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 5)
        self.assertEqual(p1c3.hp, 5)

        # test activated is cleared per action
        game_state = step_swap(game_state, Pid.P1, char_id=2)  # swap to char 2
        game_state = skip_action_round(game_state, Pid.P2)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 5)
        self.assertEqual(p1c3.hp, 5)

        # test only the active character is triggered (say if overloaded)
        game_state = apply_elemental_aura(game_state, Element.PYRO, Pid.P1)
        game_state = skip_action_round(game_state, Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL2)  # overload to char 3
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        active_id = game_state.player1.characters.get_active_character_id()
        self.assertEqual(active_id, 3)
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 5)
        self.assertEqual(p1c3.hp, 6)

        # test triggered even if death swap
        game_state = step_swap(game_state, Pid.P1, char_id=2)
        game_state = remove_all_thick_shield(game_state)
        game_state = simulate_status_dmg(game_state, 4, pid=Pid.P1)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        game_state = step_action(game_state, Pid.P1, DeathSwapAction(char_id=3))
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 0)
        self.assertEqual(p1c3.hp, 7)

        # test usages reset the next round
        game_state = grant_all_thick_shield(game_state)
        game_state = next_round_with_great_omni(game_state)
        game_state = skip_action_round_until(game_state, Pid.P2)
        game_state = step_skill(game_state, Pid.P2, CharacterSkill.SKILL1)
        p1c1, p1c2, p1c3 = game_state.player1.characters.get_characters()
        self.assertEqual(p1c1.hp, 7)
        self.assertEqual(p1c2.hp, 0)
        self.assertEqual(p1c3.hp, 8)