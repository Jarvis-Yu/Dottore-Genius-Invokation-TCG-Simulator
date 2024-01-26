import unittest

from .common_imports import *

class TestPassingOfJudgment(unittest.TestCase):
    def test_behaviour(self):
        base_state = ACTION_TEMPLATE
        base_state = PublicAddCardEffect(Pid.P1, PassingOfJudgment).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P1, TheBestestTravelCompanion).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P2, TheBestestTravelCompanion).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P2, TheBestestTravelCompanion).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P2, LotusFlowerCrisp).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P2, LightningStiletto).execute(base_state)
        base_state = PublicAddCardEffect(Pid.P2, TravelersHandySword).execute(base_state)
        base_state = replace_character(base_state, Pid.P2, Keqing, 3)

        # P1 play card and see that it doesn't affect self
        game_state = base_state
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=PassingOfJudgment,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 1})),
        ))
        p1dice_before = game_state.player1.dice
        game_state = step_action(game_state, Pid.P1, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        p1dice_after = game_state.player1.dice
        self.assertEqual(p1dice_before.num_dice(), p1dice_after.num_dice())
        
        game_state = step_skill(game_state, Pid.P1, CharacterSkill.SKILL1)
        played_state = game_state  # save this state for later
        
        ## P2 play all cards and only first "Three" "Event Card"s are affected ##
        # invalidate first event card
        p2dice_before = game_state.player2.dice
        game_state = step_action(game_state, Pid.P2, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        p2dice_after = game_state.player2.dice
        self.assertNotEqual(p2dice_before.num_dice(), p2dice_after.num_dice())

        # checks that non-event cards are not affected
        game_state = step_action(game_state, Pid.P2, CardAction(
            card=TravelersHandySword,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P2, 3),
                dice=ActualDice({Element.OMNI: 2}),
            ),
        ))
        _, _, p2c3 = game_state.player2.characters.get_characters()
        self.assertIn(TravelersHandySwordStatus, p2c3.character_statuses)

        # checks that following two event cards are affected
        game_state = step_action(game_state, Pid.P2, CardAction(
            card=LotusFlowerCrisp,
            instruction=StaticTargetInstruction(
                target=StaticTarget.from_char_id(Pid.P2, 3),
                dice=ActualDice({Element.OMNI: 1}),
            ),
        ))
        _, _, p2c3 = game_state.player2.characters.get_characters()
        self.assertNotIn(LotusFlowerCrispStatus, p2c3.character_statuses)

        game_state = step_action(game_state, Pid.P2, CardAction(
            card=LightningStiletto,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 3})),
        ))
        p2ac = p2_active_char(game_state)
        self.assertEqual(p2ac.id, 1)

        # 4th event card works
        p2dice_before = game_state.player2.dice
        game_state = step_action(game_state, Pid.P2, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        p2dice_after = game_state.player2.dice
        self.assertEqual(p2dice_before.num_dice(), p2dice_after.num_dice())

        # check that passing of judgment status doesn't live the next round
        game_state = next_round_with_great_omni(played_state)
        game_state = skip_action_round_until(game_state, Pid.P2)
        p2dice_before = game_state.player2.dice
        game_state = step_action(game_state, Pid.P2, CardAction(
            card=TheBestestTravelCompanion,
            instruction=DiceOnlyInstruction(dice=ActualDice({Element.OMNI: 2})),
        ))
        p2dice_after = game_state.player2.dice
        self.assertEqual(p2dice_before.num_dice(), p2dice_after.num_dice())
