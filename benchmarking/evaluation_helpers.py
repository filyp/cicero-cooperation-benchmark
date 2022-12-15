from collections import Counter

from constants import *


def print_all_dialogues_with_some_labels(dialogues, labels):
    dialogues_to_print = [info for info in dialogues if any(label in info["labels"] for label in labels)]
    pretty_print_the_dialogues(dialogues_to_print)


def pretty_print_the_dialogues(dialogues):
    for info in dialogues:
        if "rating" in info:
            print(f"RATING:  {info['rating']}")

        if "labels" in info:
            print("LABELS:  ", end="")
            for label in info["labels"]:
                if label[-1] in "!?":
                    # strip ! and ? from labels
                    label_stripped = label[:-1]
                    print(evaluation_legend[label_stripped][1] + label[-1], end=", ")
                else:
                    print(evaluation_legend[label][1], end=", ")
            print()

        # print(f"CICERO:  {info['cicero_power']}")
        print("\n")

        if "eval_texts" in info:
            whole_text = "".join(info["eval_texts"])
            to_print = whole_text.split("="*53)[-1]
        else:
            to_print = info["dialogue_text"]
        print(to_print.strip())
        print("\n\n=====================================================\n\n")


def print_label_stats(dialogues):
    labels = [info["labels"] for info in dialogues]
    # flatten
    labels = [label for sublist in labels for label in sublist]
    counts = Counter(labels)
    print(f"Num of examples: {len(dialogues)}")
    print(f"    |  ? |  . |  ! |")
    for label in evaluation_legend.keys():
        print(f"{label:3} | {counts[label + '?']:2} | {counts[label]:2} | {counts[label + '!']:2} |")