import unittest

from .common_imports import *

class TestTheBoarPrincess(unittest.TestCase):
    def test_substitute_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBoarPrincess: 2,
            TravelersHandySword: 3,
            GamblersEarrings: 3,
            InstructorsCap: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 3)

        game_state = base_state

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBoarPrincess,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.HYDRO: 2}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        
        # non substitution doesn't trigger
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 2}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)

        # substitution triggers
        dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 2}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 1)
        dice_after = game_state.player1.dice
        self.assertEqual((dice_after - dice_before)[Element.OMNI], 1)
        
        # non substitution doesn't trigger
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.GEO: 1}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 1)

        game_state = next_round(game_state)
        self.assertNotIn(TheBoarPrincessStatus, game_state.player1.combat_statuses)

    def test_on_death_behaviour(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBoarPrincess: 2,
            TravelersHandySword: 3,
            GamblersEarrings: 3,
            InstructorsCap: 2,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 3)

        game_state = base_state

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBoarPrincess,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 2}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        
        # self death triggers
        dice_before = game_state.player1.dice
        game_state = simulate_status_dmg(game_state, 100, pid=Pid.P1, char_id=2)
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 1)
        dice_after = game_state.player1.dice
        self.assertEqual((dice_after - dice_before)[Element.OMNI], 1)

        # test can trigger twice in one go
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBoarPrincess,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 2}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 1}),
            ),
        ))
        
        dice_before = game_state.player1.dice
        game_state = simulate_status_dmg(game_state, 100, pid=Pid.P1, char_id=2)
        self.assertNotIn(TheBoarPrincessStatus, game_state.player1.combat_statuses)
        dice_after = game_state.player1.dice
        self.assertEqual((dice_after - dice_before)[Element.OMNI], 2)

    def test_on_transfer_by_card_artifact(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBoarPrincess: 2,
            GamblersEarrings: 3,
            InstructorsCap: 2,
            BlessingOfTheDivineRelicsInstallation: 1,
        }))

        game_state = base_state

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBoarPrincess,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 1}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=GamblersEarrings,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.HYDRO: 1}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        equipped_state = game_state

        # tranfer overwriting triggers
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=BlessingOfTheDivineRelicsInstallation,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 1)

        # transfer no overwriting doesn't trigger
        game_state = equipped_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=BlessingOfTheDivineRelicsInstallation,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice.from_empty(),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)

    def test_on_transfer_by_card_weapon(self):
        base_state = ONE_ACTION_TEMPLATE
        base_state = replace_hand_cards(base_state, Pid.P1, Cards({
            TheBoarPrincess: 2,
            AquilaFavonia: 3,
            SacrificialSword: 2,
            MasterOfWeaponry: 1,
        }))
        base_state = replace_character(base_state, Pid.P1, Kaeya, 1)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 2)
        base_state = replace_character(base_state, Pid.P1, Kaeya, 3)

        game_state = base_state

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBoarPrincess,
            instruction=DiceOnlyInstruction(dice=ActualDice.from_empty()),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)

        game_state = step_action(game_state, Pid.P1, CardAction(
            card=AquilaFavonia,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 2),
                dice=ActualDice({Element.HYDRO: 3}),
            ),
        ))
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=SacrificialSword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice({Element.HYDRO: 3}),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
        equipped_state = game_state

        # tranfer overwriting triggers
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=MasterOfWeaponry,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 1),
                dice=ActualDice.from_empty(),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 1)

        # transfer no overwriting doesn't trigger
        game_state = equipped_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=MasterOfWeaponry,
            instruction=SourceTargetInstruction(
                source=StaticTarget.from_char_id(Pid.P1, 2),
                target=StaticTarget.from_char_id(Pid.P1, 3),
                dice=ActualDice.from_empty(),
            ),
        ))
        boar_status = game_state.player1.combat_statuses.just_find(TheBoarPrincessStatus)
        self.assertEqual(boar_status.usages, 2)
