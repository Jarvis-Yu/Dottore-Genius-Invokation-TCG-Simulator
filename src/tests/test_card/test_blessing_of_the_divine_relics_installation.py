import unittest

from .common_imports import *

class TestBlessingOfTheDivineRelicsInstallation(unittest.TestCase):
    def test_substitute_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            BlessingOfTheDivineRelicsInstallation: 2,
            GamblersEarrings: 3,
            InstructorsCap: 2,
        }))
        
        game_state = base_state
        game_state = UpdateCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=GamblersEarringsStatus(usages=2),
        ).execute(game_state)
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 1),
            status=InstructorsCapStatus,
        ).execute(game_state)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=BlessingOfTheDivineRelicsInstallation,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))

        p1c1, p1c2, _ = game_state.player1.characters.get_characters()
        artifact = p1c1.character_statuses.find_type(ArtifactEquipmentStatus)
        self.assertIsInstance(artifact, GamblersEarringsStatus)
        assert isinstance(artifact, GamblersEarringsStatus)
        self.assertEqual(artifact.usages, 3)
        self.assertNotIn(ArtifactEquipmentStatus, p1c2.character_statuses)

    def test_action_validity(self):
        base_state = ONE_ACTION_TEMPLATE
        
        game_state = base_state
        game_state = AddCharacterStatusEffect(
            target=StaticTarget.from_char_id(Pid.P1, 2),
            status=GamblersEarringsStatus,
        ).execute(game_state)

        # cannot choose source with no artifact
        self.assertFalse(BlessingOfTheDivineRelicsInstallation.valid_instruction(
            game_state,
            Pid.P1,
            SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 1),
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice.from_empty(),
            ),
        ))
