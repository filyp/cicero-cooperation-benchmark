import re

import openai
from cachier import cachier

from secret import API_KEY
from constants import *
from game_data_utils import build_dialogue_text

openai.api_key = API_KEY


@cachier(separate_files=True, cache_dir="../api_cache")
def completion_cached(**kwargs):
    return openai.Completion.create(**kwargs), kwargs.copy()


def get_rating(response):
    # note that some ratings are decimal numbers, e.g. "7.5/10"
    rating_regex = re.compile(
        r"(\d+\.?\d*)\/10"
        "|(\d+\.?\d*) out of 10"
        "|as a (\d+\.?\d*)"
        "|rated a (\d+\.?\d*)"
        "|rating of (\d+\.?\d*)"
        "|at (\d+\.?\d*)"
        "|at a (\d+\.?\d*)"
        "|is (\d+\.?\d*)"
        "|was (\d+\.?\d*)"
        "|a (\d+\.?\d*)"
        "|would be (\d+\.?\d*)"
        "|was rated (\d+\.?\d*)"
        "|as (\d+\.?\d*)"
        "|as being (\d+\.?\d*)"
    )

    rating_groups = rating_regex.search(response)
    if rating_groups is None:
        # try out an even simpler regex
        rating_regex = re.compile(r"(\d+\.?\d*)")
        # find all matches
        rating_groups = rating_regex.findall(response)
        # if there are multiple matches, we can't tell which one is the rating
        if len(rating_groups) != 1:
            return None
        rating = rating_groups[0]
    else:
        # only one of those groups will be non-None
        rating = next(filter(None, rating_groups.groups()))

    rating = float(rating)
    if rating < 1 or rating > 10:
        return None
    return rating


assert get_rating("I would rate Cicero as a 7.5") == 7.5
assert get_rating("I would rate Cicero as a 7") == 7
assert get_rating("I would rate Cicero as a 7.5/10") == 7.5
assert get_rating("I would rate Cicero as a 7 out of 10.") == 7
assert get_rating("I would give a rating of 7") == 7
assert get_rating("I would estimate it at 7") == 7
assert get_rating("7") == 7
assert get_rating("7 7") == None
assert get_rating("On a scale from 1 to 10, I would rate it at 7") == 7
assert get_rating("11") == None
assert get_rating("0") == None


def get_rating_for_dialogue(dialogue, cicero_power, human_power, prompt_templates, model):
    dialogue_text = build_dialogue_text(dialogue)
    eval_texts = []

    for prompt_template in prompt_templates:
        prompt = prompt_template.format(cicero_power=cicero_power, human_power=human_power)
        eval_texts.append(prompt)

        full_response, _kwargs = completion_cached(
            model=model,
            prompt=dialogue_text + "".join(eval_texts),
            max_tokens=300,
            temperature=0,
        )
        response = full_response["choices"][0]["text"]
        eval_texts.append(response)

    rating = get_rating(eval_texts[-1])
    return dialogue_text, eval_texts, cicero_power, human_power, rating
