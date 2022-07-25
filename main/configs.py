"""Different configs, mostly domain-specific. Used in `services.py` and `scripts.py`"""

from collections import namedtuple

# Minimum ratio of right answers to say that the answer is partially correct
EVALUATE_THRASHHOLD = 0.2

# Scales for checking answers with multiple answers
scales_dict = {
    'DEFAULT': (0, 0.5, 1, 1.5, 2, 2.5)
}
Scales = namedtuple('Scales', scales_dict)
SCALES = Scales(**scales_dict)

QUESTIONS_PER_PAGE = 3