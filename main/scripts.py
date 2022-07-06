from typing import Tuple

from .services import Compare

def points_from_matrix(compare_matrix: Tuple[Compare, ...]) -> Tuple[int, int]:
    user_points = sum(compare_matrix)
    max_points = len(compare_matrix)
    return user_points, max_points


def counter_p2(
    right_answer: str,
    user_answer: str,
    max_score,
    scale: tuple = (0, 0.5, 1, 1.5, 2, 2.5),
    var_set = 'абвгд'
) -> Tuple[Tuple[Compare, ...], int, int]
    """Implements checking of multiple choice questions in format like `abd`, where correct answer is `bc`"""

    compare_matrix = []

    for letter in var_set:
        
        right_letter = letter if letter in right_answer else ''
        user_letter = letter if letter in user_answer else ''
        is_right = right_letter == user_letter
        compare_matrix.append(Compare(right_answer, user_answer, is_right))

    user_points, max_points = points_from_matrix(compare_matrix)
    
    user_default_score = user_points / max_points * max_score
    
    if scale[-1] != max_score:
        message = (
            'Maximum score should be equal to the last value in the scale.',
            f'However, maximum score {max_score} and scale {scale} were given.'
        )
        raise ValueError(message)
    elif len(scale) != len(var_set):
        pass
    
    
    return compare_matrix, user_default_score, user_score