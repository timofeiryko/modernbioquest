"""Datastructures for parsing pdf"""

from dataclasses import dataclass
from typing import List

@dataclass
class QuestionDraft:
    title: str
    text: str
    part: int
    number: int

@dataclass
class CleanedQuestion:
    question: QuestionDraft
    text: str
    answer_variants: List[str]

