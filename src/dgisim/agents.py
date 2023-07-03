import random
from typing import Optional, Iterable, TYPE_CHECKING

from .action.action import *
from .action.action_generator import *
from .action.types import DecidedChoiceType
from .card.card import *
from .character.character_skill_enum import CharacterSkill
from .dices import AbstractDices, ActualDices
from .effect.effect import *
from .element.element import Element
from .phase.action_phase import ActionPhase
from .phase.card_select_phase import CardSelectPhase
from .phase.end_phase import EndPhase
from .phase.roll_phase import RollPhase
from .phase.starting_hand_select_phase import StartingHandSelectPhase
from .player_agent import PlayerAgent
from .state.enums import PID
from .state.game_state import GameState


class NoneAgent(PlayerAgent):
    pass


class LazyAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(char_id=1)

        elif isinstance(curr_phase, RollPhase):
            raise Exception("No Action Defined")

        elif isinstance(curr_phase, ActionPhase):
            return EndRoundAction()

        else:
            raise Exception("No Action Defined")


class PuppetAgent(PlayerAgent):
    def __init__(self, actions: Optional[list[PlayerAction]] = None) -> None:
        if actions is None:
            self._actions = []
        else:
            self._actions = actions

    def inject_action(self, action: PlayerAction) -> None:
        self._actions.append(action)

    def inject_actions(self, actions: list[PlayerAction]) -> None:
        self._actions += actions

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        assert self._actions
        return self._actions.pop(0)

    def clear(self) -> None:
        self._actions = []

    def __str__(self) -> str:
        return f"PuppetAgent[{', '.join(str(action) for action in self._actions)}]"


class HardCodedRandomAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            _, selected_cards = game_state.get_player(
                pid).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
            return CardSelectAction(selected_cards=selected_cards)

        elif isinstance(curr_phase, StartingHandSelectPhase):
            return CharacterSelectAction(char_id=1)

        elif isinstance(curr_phase, RollPhase):
            raise Exception("No Action Defined")

        elif isinstance(curr_phase, ActionPhase):
            selection = random.random()
            me = game_state.get_player(pid)
            available_dices = me.get_dices()
            active_character = me.get_active_character()

            assert active_character is not None

            # death swap
            if active_character.defeated():
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if alive_ids:
                    return DeathSwapAction(char_id=random.choice(alive_ids))
                else:
                    raise Exception("Game should end here but not implemented(NOT REACHED)")

            # food card
            character_injured = active_character.get_hp() < active_character.get_max_hp()
            if selection < 1:
                cards = me.get_hand_cards()
                card: Optional[type[Card]]
                tmp_dices = ActualDices({})

                if cards.contains(SweetMadame) and character_injured:
                    card = SweetMadame
                    tmp_dices = ActualDices({Element.OMNI: 0})
                elif cards.contains(MondstadtHashBrown) and character_injured:
                    tmp_dices = ActualDices({Element.OMNI: 1})
                    card = MondstadtHashBrown
                elif cards.contains(MushroomPizza) and character_injured:
                    tmp_dices = ActualDices({Element.OMNI: 1})
                    card = MushroomPizza
                else:
                    card = None

                if card is not None \
                        and not active_character.satiated() \
                        and (available_dices - tmp_dices).is_legal():
                    return CardAction(
                        card=card,
                        instruction=StaticTargetInstruction(
                            dices=tmp_dices,
                            target=StaticTarget(
                                pid,
                                ZONE.CHARACTERS,
                                active_character.get_id(),
                            )
                        )
                    )

            # swap character
            if selection < 0.2:
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 1,
                }))
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if dices is not None and alive_ids:
                    return SwapAction(
                        char_id=random.choice(alive_ids),
                        instruction=DiceOnlyInstruction(dices=dices),
                    )

            if selection < 1 and active_character.can_cast_skill():
                # elemental burst
                if active_character.get_energy() == active_character.get_max_energy() \
                        and CharacterSkill.ELEMENTAL_BURST in active_character.skills():
                    dices = available_dices.basically_satisfy(
                        active_character.skill_cost(CharacterSkill.ELEMENTAL_BURST)
                    )
                    if dices is not None:
                        return SkillAction(
                            skill=CharacterSkill.ELEMENTAL_BURST,
                            instruction=DiceOnlyInstruction(dices=dices),
                        )

                # elemental skill2
                if selection < 0.7 and CharacterSkill.ELEMENTAL_SKILL2 in active_character.skills():
                    dices = available_dices.basically_satisfy(
                        active_character.skill_cost(CharacterSkill.ELEMENTAL_SKILL2)
                    )
                    if dices is not None:
                        return SkillAction(
                            skill=CharacterSkill.ELEMENTAL_SKILL2,
                            instruction=DiceOnlyInstruction(dices=dices),
                        )

                # elemental skill1
                if selection < 0.7 and CharacterSkill.ELEMENTAL_SKILL1 in active_character.skills():
                    dices = available_dices.basically_satisfy(
                        active_character.skill_cost(CharacterSkill.ELEMENTAL_SKILL1)
                    )
                    if dices is not None:
                        return SkillAction(
                            skill=CharacterSkill.ELEMENTAL_SKILL1,
                            instruction=DiceOnlyInstruction(dices=dices),
                        )

                # normal attack
                if selection < 1 and CharacterSkill.NORMAL_ATTACK in active_character.skills():
                    dices = available_dices.basically_satisfy(
                        active_character.skill_cost(CharacterSkill.NORMAL_ATTACK)
                    )
                    if dices is not None:
                        return SkillAction(
                            skill=CharacterSkill.NORMAL_ATTACK,
                            instruction=DiceOnlyInstruction(dices=dices),
                        )

            # swap character
            if selection < 0.8:
                dices = available_dices.basically_satisfy(AbstractDices({
                    Element.ANY: 1,
                }))
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if dices is not None and alive_ids:
                    return SwapAction(
                        char_id=random.choice(alive_ids),
                        instruction=DiceOnlyInstruction(dices=dices),
                    )

            return EndRoundAction()

        elif isinstance(curr_phase, EndPhase):
            me = game_state.get_player(pid)
            active_character = me.just_get_active_character()

            # death swap
            if active_character.defeated():
                characters = me.get_characters()
                alive_ids = characters.alive_ids()
                active_id = characters.get_active_character_id()
                assert active_id is not None
                if active_id in alive_ids:
                    alive_ids.remove(active_id)
                if alive_ids:
                    return DeathSwapAction(char_id=random.choice(alive_ids))
                else:
                    raise Exception("Game should end here but not implemented(NOT REACHED)")

            raise Exception("NOT REACHED")

        else:
            raise Exception(f"No Action Defined, phase={curr_phase}")


class RandomAgent(PlayerAgent):
    _NUM_PICKED_CARDS = 3

    def _card_select_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        _, selected_cards = game_state.get_player(
            pid
        ).get_hand_cards().pick_random_cards(self._NUM_PICKED_CARDS)
        return CardSelectAction(selected_cards=selected_cards)

    def _starting_hand_select_phase(
            self,
            history: list[GameState],
            pid: PID
    ) -> PlayerAction:
        return CharacterSelectAction(char_id=random.randint(1, 3))

    def _roll_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        raise Exception("No Action Defined")

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
                choice = random.choice(choices)
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, AbstractDices):
                optional_choice = action_generator.dices_available().basically_satisfy(choices)
                if optional_choice is None:
                    raise Exception(f"There's not enough dices for {choices} from "
                                    + f"{action_generator.dices_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                choice = optional_choice
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()

    def _action_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        me = game_state.get_player(pid)
        active_character = me.just_get_active_character()

        # death swap
        if game_state.swap_checker().should_death_swap():
            swap_action_generator = game_state.swap_checker().action_generator(pid)
            assert swap_action_generator is not None
            player_action = self._random_action_generator_chooser(swap_action_generator)
            return player_action

        # elemental tuning
        decision = random.random()
        if decision < 0.3:
            elem_tuning_generator = game_state.elem_tuning_checker().action_generator(pid)
            if elem_tuning_generator is not None:
                player_action = self._random_action_generator_chooser(elem_tuning_generator)
                return player_action

        # cast skill
        decision = random.random()
        if decision < 0.5:
            skill_action_generator = game_state.skill_checker().action_generator(pid)
            if skill_action_generator is not None:
                player_action = self._random_action_generator_chooser(skill_action_generator)
                return player_action

        # play card
        decision = random.random()
        if decision < 0.5:
            cards = game_state.get_player(pid).get_hand_cards()
            cards_list = list(cards)
            random.shuffle(cards_list)
            action_generator = next(
                (
                    act_generator
                    for act_generator in (
                        card.action_generator(game_state, pid) for card in cards
                    )
                    if act_generator is not None
                ),
                None
            )
            if action_generator is not None:
                player_action = self._random_action_generator_chooser(action_generator)
                return player_action

        # swap
        decision = random.random()
        if decision < 0.5:
            swap_action_generator = game_state.swap_checker().action_generator(pid)
            if swap_action_generator is not None:
                player_action = self._random_action_generator_chooser(swap_action_generator)
                return player_action

        return EndRoundAction()

    def _end_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]

        # death swap
        if game_state.swap_checker().should_death_swap():
            swap_action_generator = game_state.swap_checker().action_generator(pid)
            assert swap_action_generator is not None
            player_action = self._random_action_generator_chooser(swap_action_generator)
            return player_action

        raise Exception("NOT REACHED")

    def choose_action(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        curr_phase = game_state.get_phase()

        if isinstance(curr_phase, CardSelectPhase):
            return self._card_select_phase(history, pid)
        elif isinstance(curr_phase, StartingHandSelectPhase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, RollPhase):
            return self._starting_hand_select_phase(history, pid)
        elif isinstance(curr_phase, ActionPhase):
            return self._action_phase(history, pid)
        elif isinstance(curr_phase, EndPhase):
            return self._end_phase(history, pid)

        raise NotImplementedError


class CustomChoiceAgent(RandomAgent):
    def __init__(
            self,
            prompt_handler: Callable[[str, str], None],
            choose_handler: Callable[[Iterable[DecidedChoiceType]], DecidedChoiceType],
            any_handler: Callable[[Iterable[Any]], Any],
    ) -> None:
        self._prompt_handler = prompt_handler
        self._choose_handler = choose_handler
        self._any_handler = any_handler

    def _random_action_generator_chooser(self, action_generator: ActionGenerator) -> PlayerAction:
        while not action_generator.filled():
            choices = action_generator.choices()
            choice: DecidedChoiceType  # type: ignore
            if isinstance(choices, tuple):
                choice = self._choose_handler(choices)
                action_generator = action_generator.choose(choice)
            elif isinstance(choices, AbstractDices):
                optional_choice = action_generator.dices_available().basically_satisfy(choices)
                if optional_choice is None:
                    raise Exception(f"There's not enough dices for {choices} from "
                                    + f"{action_generator.dices_available()} at game_state:"
                                    + f"{action_generator.game_state}")
                choice = optional_choice
                action_generator = action_generator.choose(choice)
            else:
                raise NotImplementedError
        return action_generator.generate_action()

    def _action_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]
        me = game_state.get_player(pid)
        active_character = me.just_get_active_character()

        self._prompt_handler("info", f"Player{pid.value}'s Action Time!")

        player_action: None | PlayerAction = None
        action_generator: None | ActionGenerator

        # death swap
        if game_state.swap_checker().should_death_swap():
            swap_action_generator = game_state.swap_checker().action_generator(pid)
            assert swap_action_generator is not None
            self._prompt_handler("info", "Death Swap Action")
            player_action = self._random_action_generator_chooser(swap_action_generator)
            return player_action

        choices: tuple[str, ...] = ("Card", "Skill", "Swap", "Elemental Tuning", "EndRound")
        choice: Any
        while player_action is None:
            choice = self._any_handler(choices)

            if choice == "Card":
                cards = game_state.get_player(pid).get_hand_cards()
                usable_card_gen_pair = dict([
                    (card, act_gen)
                    for card, act_gen in (
                        (card, card.action_generator(game_state, pid))
                        for card in cards
                    )
                    if act_gen is not None
                ])
                if not usable_card_gen_pair:
                    self._prompt_handler("info", "No card available")
                    continue
                choice = self._any_handler(usable_card_gen_pair.keys())
                action_generator = usable_card_gen_pair[choice]
                player_action = self._random_action_generator_chooser(action_generator)

            elif choice == "Skill":
                action_generator = game_state.skill_checker().action_generator(pid)
                if action_generator is None:
                    self._prompt_handler("info", "No skill available")
                    continue
                player_action = self._random_action_generator_chooser(action_generator)

            elif choice == "Swap":
                action_generator = game_state.swap_checker().action_generator(pid)
                if action_generator is None:
                    self._prompt_handler("info", "Swapping is unavailable")
                    continue
                player_action = self._random_action_generator_chooser(action_generator)

            elif choice == "Elemental Tuning":
                action_generator = game_state.elem_tuning_checker().action_generator(pid)
                if action_generator is None:
                    self._prompt_handler("info", "There's no dice or card for tuning")
                    continue
                player_action = self._random_action_generator_chooser(action_generator)

            elif choice == "EndRound":
                player_action = EndRoundAction()

            else:
                self._prompt_handler("error", f"Uncaught choice {choice}")

        return player_action

    def _end_phase(self, history: list[GameState], pid: PID) -> PlayerAction:
        game_state = history[-1]

        self._prompt_handler("info", f"Player{pid.value}'s Action Time!")

        # death swap
        if game_state.swap_checker().should_death_swap():
            swap_action_generator = game_state.swap_checker().action_generator(pid)
            assert swap_action_generator is not None
            self._prompt_handler("info", "Death Swap Action")
            player_action = self._random_action_generator_chooser(swap_action_generator)
            return player_action

        raise Exception("NOT REACHED")
