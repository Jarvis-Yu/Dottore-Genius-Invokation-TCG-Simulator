import inspect
import os
import pickle
import random
from collections import defaultdict
from dataclasses import dataclass, field, fields
from enum import Enum
from itertools import chain
from pprint import pprint
from timeit import timeit
from typing import Any

from tqdm import tqdm

from src.package import StaticTarget, DamageType
from src.dgisim.agents import RandomAgent
from src.dgisim.card import card as cd
from src.dgisim.character.character import *
from src.dgisim.character.characters import Characters
from src.dgisim.dice import ActualDice, AbstractDice
from src.dgisim.element import Element
from src.dgisim.encoding.encoding_plan import encoding_plan
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.summon import summon as sm
from src.dgisim.state.game_state import GameState
from src.dgisim.status import status as st
from src.dgisim.support import support as sp

stts = []
sms = []
sps = []

for name in st.__all__:
    status_class = getattr(st, name)
    try:
        status = status_class()
        stts.append(status)
    except Exception:
        continue

for name in sm.__all__:
    summon_class = getattr(sm, name)
    try:
        summon = summon_class()
        sms.append(summon)
    except Exception:
        continue

for name in sp.__all__:
    support_class = getattr(sp, name)
    try:
        support = support_class(sid=0)
        sps.append(support)
    except Exception:
        continue

status_field_types = set()

type_size_map = defaultdict(lambda: 1000)
type_size_map.update({
    int: 1,
    bool: 1,
    Element: 1,
    Enum: 1,
    type(None): 1,
    type: 1,
    StaticTarget: 3,
    ActualDice: 4,
    DamageType: 9,
})

stt_size_list: list[tuple[int, st.Status]] = []
sms_size_list: list[tuple[int, sm.Summon]] = []
sps_size_list: list[tuple[int, sp.Support]] = []

for status in stts:
    curr_max = 0
    for field_val in [
        status.__getattribute__(field.name)
        for field in fields(status)
    ]:
        status_field_types.add(type(field_val))
        curr_max += type_size_map[type(field_val)]
    stt_size_list.append((curr_max, status))

for summon in sms:
    curr_max = 0
    for field_val in [
        summon.__getattribute__(field.name)
        for field in fields(summon)
    ]:
        status_field_types.add(type(field_val))
        curr_max += type_size_map[type(field_val)]
    sms_size_list.append((curr_max, summon))

for support in sps:
    curr_max = 0
    for field_val in [
        support.__getattribute__(field.name)
        for field in fields(support)
    ]:
        status_field_types.add(type(field_val))
        curr_max += type_size_map[type(field_val)]
    sps_size_list.append((curr_max, support))

stt_size_list.sort(key=lambda k: (k[0], k[1].__class__.__name__), reverse=True)
sms_size_list.sort(key=lambda k: (k[0], k[1].__class__.__name__), reverse=True)
sps_size_list.sort(key=lambda k: (k[0], k[1].__class__.__name__), reverse=True)

type_size_map[st.Status] = max(stt_size_list[0][0], sms_size_list[0][0], sps_size_list[0][0])

# GameState testing...
all_states: list[GameState] = []
runs = 100
print("Generating game states...")
for _ in tqdm(range(runs)):
    game_state = GameState.from_default()
    gsm = GameStateMachine(game_state, RandomAgent(), RandomAgent())
    gsm.run()
    all_states.extend(gsm.get_history())

encoding_length = set()

@dataclass
class Data:
    total_runs: int = 0
    max_effect_size: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    max_effects_num: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    max_char_hidden_size: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    max_char_stt_size: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    max_combat_hidden_size: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    max_combat_stt_size: dict[int, int] = field(default_factory=lambda: defaultdict(int))

data = Data()
if os.path.exists("scripts/py/encoding_limit/encoding_limit.pickle"):
    with open("scripts/py/encoding_limit/encoding_limit.pickle", "rb") as f:
        saved_data = pickle.load(f)
        try:
            data.total_runs = saved_data.total_runs
        except Exception:
            pass
        try:
            data.max_effect_size = saved_data.max_effect_size
        except Exception:
            pass
        try:
            data.max_effects_num = saved_data.max_effects_num
        except Exception:
            pass
        try:
            data.max_char_hidden_size = saved_data.max_char_hidden_size
        except Exception:
            pass
        try:
            data.max_char_stt_size = saved_data.max_char_stt_size
        except Exception:
            pass
        try:
            data.max_combat_hidden_size = saved_data.max_combat_hidden_size
        except Exception:
            pass
        try:
            data.max_combat_stt_size = saved_data.max_combat_stt_size
        except Exception:
            pass

effect_field_types = set()

print("Analyzing game states...")
for game_state in tqdm(all_states):
    game_state_encoding = game_state.encoding(encoding_plan)
    encoding_length.add(len(game_state_encoding))
    data.max_effects_num[len(game_state.get_effect_stack()._effects)] += 1

    # Effects
    for effect in game_state.get_effect_stack()._effects:
        effect_size = 0
        for field_val in [
            effect.__getattribute__(field.name)
            for field in fields(effect)
        ]:
            eff_type = type(field_val)
            if isinstance(field_val, Enum):
                effect_field_types.add(Enum)
                eff_type = Enum
            elif inspect.isclass(field_val):
                if issubclass(field_val, st.Status):
                    effect_field_types.add(st.Status.__name__)
                elif issubclass(field_val, cd.Card):
                    effect_field_types.add(cd.Card.__name__)
                else:
                    effect_field_types.add(field_val.__name__)
            elif isinstance(field_val, st.Status):
                effect_field_types.add(st.Status)
                eff_type = st.Status
            else:
                effect_field_types.add(type(field_val))
            effect_size += type_size_map[eff_type]
        data.max_effect_size[effect_size] += 1

    # Statuses
    for char in chain(game_state.get_player1().get_characters(), game_state.get_player2().get_characters()):
        data.max_char_hidden_size[len(char.get_hidden_statuses()._statuses)] += 1
        data.max_char_stt_size[len(char.get_character_statuses()._statuses)] += 1
    for player in (game_state.get_player1(), game_state.get_player2()):
        data.max_combat_hidden_size[len(player.get_hidden_statuses()._statuses)] += 1
        data.max_combat_stt_size[len(player.get_combat_statuses()._statuses)] += 1

data.total_runs += runs

with open("scripts/py/encoding_limit/encoding_limit.pickle", "wb") as f:
    pickle.dump(data, f)

print()
print(f"Total runs: {data.total_runs}")
print(f"Status max size: {stt_size_list[0][0]}")
print(f"Summon max size: {sms_size_list[0][0]}")
print(f"Support max size: {sps_size_list[0][0]}")
print(f"Max effect size: {max(data.max_effect_size.keys())}")
print(f"Max effects num: {max(data.max_effects_num.keys())}")
print(f"Max char hidden size: {max(data.max_char_hidden_size.keys())}")
print(f"Max char stt size: {max(data.max_char_stt_size.keys())}")
print(f"Max combat hidden size: {max(data.max_combat_hidden_size.keys())}")
print(f"Max combat stt size: {max(data.max_combat_stt_size.keys())}")
print(f"Encoding length(s): {encoding_length}")

print()
print(f"Status field types: {status_field_types}")
print(f"Effect field types: {effect_field_types}")

#### Plotting ####
import matplotlib.pyplot as plt

def plot_dict(d: dict[int, int], title: str):
    total = sum(d.values())
    threshold = total / len(d) * 0.1
    plt.figure(figsize=(10, 10))
    bars = plt.bar(d.keys(), d.values())
    plt.xticks(list(d.keys()))
    for val, bar in zip(d.values(), bars):
        if val > threshold:
            continue
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, str(val), ha='center', va='bottom')
    plt.title(title)
    plt.savefig(f"scripts/py/encoding_limit/{title}.png")
    plt.clf()

plot_dict(data.max_effect_size, "Effect size distribution")
plot_dict(data.max_effects_num, "Effects num distribution")
plot_dict(data.max_char_hidden_size, "Character hidden statuses size distribution")
plot_dict(data.max_char_stt_size, "Character statuses size distribution")
plot_dict(data.max_combat_hidden_size, "Combat hidden statuses size distribution")
plot_dict(data.max_combat_stt_size, "Combat statuses size distribution")
