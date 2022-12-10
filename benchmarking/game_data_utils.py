import re
import random
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

from constants import *


def get_games():
    game_data_path = Path("../diplomacy_cicero/data/cicero_redacted_games")
    game_files = list(game_data_path.glob("*.json"))

    for game_file in game_files:
        game = json.loads(game_file.read_text())
        game_id = game_file.name.split("_")[1]
        cicero_power = game_file.name.split("_")[2]
        yield game, cicero_power, game_id


def get_per_power_dialogues(game, cicero_power):
    """
    For each power, returns a chronological list of messages sent to or from that power, throughout the whole game.
    Each dialogue is a list of lists, where each sublist is one phase.

    Also includes messages sent to "ALL", but only if the sender is the power or cicero.
    """
    dialogues = dict()

    for power_name in power_names:
        dialogues[power_name] = []

        for phase in game["phases"]:
            dialogues[power_name].append([])
            for message in phase["messages"]:  # messages are chronologically ordered
                if (
                    message["sender"] == power_name
                    and message["recipient"] == cicero_power
                    or message["sender"] == cicero_power
                    and message["recipient"] == power_name
                    or message["sender"] == power_name
                    and message["recipient"] == "ALL"
                    or message["sender"] == cicero_power
                    and message["recipient"] == "ALL"
                ):
                    dialogues[power_name][-1].append(message)

    del dialogues[
        cicero_power
    ]  # this contains all the messages, because cicero is always either sender or recipient
    return dialogues


def build_dialogue_text(message_list):
    dialogue_text = ""
    for message in message_list:
        if message["recipient"] == "ALL":
            dialogue_text += f'{message["sender"]} -> ALL:  {message["message"]}\n\n'
        else:
            dialogue_text += f'{message["sender"] + ":":8}  {message["message"]}\n\n'
    return dialogue_text


def is_phase_long_enough(
    phase, cicero_power, human_power, min_cicero_messages=2, min_human_messages=2
):
    cicero_messages = 0
    human_messages = 0
    for message in phase:
        if message["sender"] == cicero_power:
            cicero_messages += 1
        elif message["sender"] == human_power:
            human_messages += 1
    return (
        cicero_messages >= min_cicero_messages and human_messages >= min_human_messages
    )


def get_all_phase_dialogues():
    """
    Generates a tuple of (phase, cicero_power, human_power) for each phase in each game.

    phase is a list of messages forming a one-phase dialogue,
    where each message is a dict with keys "sender", "recipient", and "message"
    """
    for game, cicero_power, game_id in get_games():
        dialogues = get_per_power_dialogues(game, cicero_power)

        for human_power, dialogue in dialogues.items():
            for phase in dialogue:
                if is_phase_long_enough(phase, cicero_power, human_power):
                    yield phase, cicero_power, human_power, game_id
