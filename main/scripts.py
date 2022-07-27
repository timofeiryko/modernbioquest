"""Fust domain related scripts, not related to ORM at all"""

from .configs import SCALES

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


def generate_question_link(
    competition: str, stage: str,
    year: int, grade: int, number: int
) -> str:
    return '-'.join([
        competition, stage,
        str(year), str(grade), str(number)
    ])