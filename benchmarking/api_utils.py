import re
from concurrent.futures import ThreadPoolExecutor

import openai
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from cachier import cachier

from secret import API_KEY
from constants import *

openai.api_key = API_KEY


@cachier(separate_files=True, cache_dir="../api_cache")
def completion_cached(**kwargs):
    return openai.Completion.create(**kwargs)


def get_rating(response):
    # note that some ratings are decimal numbers, e.g. "7.5/10"
    rating_regex = re.compile(
        r"(\d+\.?\d*)\/10|"
        "(\d+\.?\d*) out of 10|"
        "as a (\d+\.?\d*)|"
        "rated a (\d+\.?\d*)|"
        "rating of (\d+\.?\d*)|"
        "at (\d+\.?\d*)|"
        "at a(\d+\.?\d*)|"
        "is (\d+\.?\d*)|"
        "was (\d+\.?\d*)|"
        "a (\d+\.?\d*)"
    )

    rating_groups = rating_regex.search(response)
    if rating_groups is None:
        return None
    # only one of those groups will be non-None
    rating = next(filter(None, rating_groups.groups()))
    rating = int(float(rating))
    if rating < 1 or rating > 10:
        return None
    return rating


assert get_rating("I would rate Cicero as a 7.5") == 7
assert get_rating("I would rate Cicero as a 7") == 7
assert get_rating("I would rate Cicero as a 7.5/10") == 7
assert get_rating("I would rate Cicero as a 7 out of 10.") == 7
assert get_rating("I would give a rating of 7") == 7
assert get_rating("I would estimate it at 7") == 7