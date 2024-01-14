import unittest

from .common_imports import *

class TestMasterOfWeaponry(unittest.TestCase):
    def test_substitute_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            MasterOfWeaponry: 2,
            AquilaFavonia: 3,
            SacrificialSword: 1,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 3)
        
        game_state = base_state
        game_state = OverrideCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=AquilaFavoniaStatus(usages=0),
        ).execute(game_state)
        game_state = OverrideCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 1),
            status=SacrificialSwordStatus(usages=0),
        ).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=MasterOfWeaponry,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))

        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        artifact = p1c1.character_statuses.find_type(WeaponEquipmentStatus)
        self.assertIsInstance(artifact, AquilaFavoniaStatus)
        assert isinstance(artifact, AquilaFavoniaStatus)
        self.assertEqual(artifact.usages, 2)
        self.assertNotIn(WeaponEquipmentStatus, p1c2.character_statuses)

    def test_action_validity(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Klee, 3)
        
        game_state = base_state
        game_state = OverrideCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=AquilaFavoniaStatus(usages=0),
        ).execute(game_state)

        # cannot choose source with no weapon
        self.assertFalse(MasterOfWeaponry.valid_instruction(
            game_state,
            Pid.P1,
            SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 1),
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice.from_empty(),
            ),
        ))

        # cannot transfer weapon to character who cannot equip such weapon
        self.assertFalse(MasterOfWeaponry.valid_instruction(
            game_state,
            Pid.P1,
            SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice.from_empty(),
            ),
        ))
