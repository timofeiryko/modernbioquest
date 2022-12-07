"""Different configs, mostly domain-specific. Used in `services.py` and `scripts.py`"""

from collections import namedtuple

# Minimum ratio of right answers to say that the answer is partially correct
EVALUATE_THRASHHOLD = 0.2

# Scales for checking answers with multiple answers
SCALES = {
    'DEFAULT': (0.0, 0.5, 1.0, 1.5, 2.0, 2.5),
    'LATEST_ZAKL_P2': (0.0, 0.0, 0.5, 1.0, 1.5, 2.5),
    'LATEST_ZAKL_P3': (0.0, 0.0, 1.0, 2.0, 3.0, 5.0)
}

QUESTIONS_PER_PAGE = 10

STAGE_SLUGS = {
    'Отборочный': 'otbor',
    'Муниципальный': 'mun',
    'Региональный': 'reg',
    'Заключительный': 'zakl',
}

FUZZ_TRESHOLD = 80