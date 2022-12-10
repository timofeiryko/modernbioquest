"""Just domain related scripts, not related to ORM at all"""

import string

from thefuzz import fuzz

from .configs import SCALES, STAGE_SLUGS

def get_max_score_zakl(part: int, p2_scale: str = 'LATEST_ZAKL_P2', p3_scale: str = 'LATEST_ZAKL_P3') -> float:

    if part == 1:
        return 1.0
    
    elif part == 2:
        return SCALES[p2_scale][-1]

    elif part == 3:
        return SCALES[p3_scale][-1]

    elif part == 4 or part == 5:
        return 0.0

    else:
        raise ValueError(f'WRONG PART {part}!')

# We don't create any abstraction for the stage and simply store the slugs in the config,
# because we don't need to change these slugs and we rarely need new slug
def get_stage_slug(stage: str) -> str:
    return STAGE_SLUGS[stage] if stage in STAGE_SLUGS else 'stage'

def get_stage_name(stage_slug: str) -> str:
    for stage, slug in STAGE_SLUGS.items():
        if slug == stage_slug:
            return stage
    return ''

def generate_question_link(
    competition: str, stage: str,
    year: int, grade: int, part: int, number: int
) -> str:
    return '-'.join([
        competition, stage,
        str(year), str(grade), str(part), str(number)
    ])

def clean_query(query: str) -> str:
    """Cleans the query from the punctuation and makes it lowercase."""
    
    # remove punctuation
    query = query.translate(str.maketrans('', '', string.punctuation))

    return query.lower()

def fuzz_search(query: str, big_string: str, treshold: int) -> bool:
    """Fuzzy search of the substring in the string."""

    query, big_string = clean_query(query), clean_query(big_string)

    if len(query) > len(big_string):
        return False
    
    return fuzz.partial_ratio(query, big_string) >= treshold

    