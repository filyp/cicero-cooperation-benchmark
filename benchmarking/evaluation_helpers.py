from collections import Counter

from constants import *


def print_all_dialogues_with_some_labels(dialogues, labels):
    for info in dialogues:
        if any(label in info["labels"] for label in labels):
            print(f"( Cicero is: {info['cicero_power']} )")
            print(info["dialogue_text"])
            print(" ".join(info["labels"]))
            print("\n=====================================================\n\n")


def print_label_stats(dialogues):
    labels = [info["labels"] for info in dialogues]
    # flatten
    labels = [label for sublist in labels for label in sublist]
    counts = Counter(labels)
    print(f"Num of examples: {len(dialogues)}")
    print(f"    |  ? |  . |  ! |")
    for label in evaluation_legend.keys():
        print(f"{label:3} | {counts[label + '?']:2} | {counts[label]:2} | {counts[label + '!']:2} |")