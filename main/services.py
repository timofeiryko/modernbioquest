"""Custom classes and functions for domain logic (aka business logic).
Most of this logic is related with objects, data stuctures etc.
The `scripts.py` is the other place where domain logic is placed (just some tools, not related with particular abstractions at all)."""

from django.http import Http404
from django.db.models import Q

from .models import Question, Competition, Section
from .scripts import generate_question_link, get_stage_name, clean_query, fuzz_search
from .configs import FUZZ_TRESHOLD

from typing import List

def extend_question_text(question: Question) -> str:
    """Extends question text with its title and answer variants."""

    full_text = question.text
    if question.title:
        full_text += ('\n' + question.title)

    answer_variants = question.answer_variants()[0]
    for answer_variant in answer_variants:
        full_text += ('\n' + answer_variant.label + ' ' + answer_variant.text)

    full_text += ('\n' + ' '.join([section.name for section in question.sections.all()]))
    full_text += ('\n' + ' '.join([topic.name for topic in question.topics.all()]))


    full_text += ('\n' + question.competition.name)
    full_text += ('\n' + question.stage)

    return full_text

def filter_questions_by_query(query: str, questions):
    """Returns questions by search query."""

    # Such itertive search is inefficient, but icontains for non-english languages is not supported by sqlite
    # In addition, fuzz search allows to perform easy not exact search
    matching_pks = []
    for question in questions:
        text = extend_question_text(question)
        # TODO Something more smart like elastic search or SpaCy
        if fuzz_search(query, text, treshold=FUZZ_TRESHOLD):
            matching_pks.append(question.pk)

    questions = questions.filter(pk__in=matching_pks)

    return questions

def get_questions_by_sections(sections: List[Section]):
    """Returns questions by their sections."""

    # get all questions by their sections
    questions = Question.objects.filter(sections__in=sections, listed=True).order_by('-id')

    return questions

def get_question_by_link(link: str) -> Question:
    """Returns question by its link. Raises 404 if question doesn't exist."""

    # link is defined by generate_question_link function from scripts.py
    print(f'trying to get question by link: {link}')
    competition_slug, stage_slug, year, grade, part, number = link.split('-')
    year, grade, part, number = int(year), int(grade), int(part), int(number)
    stage = get_stage_name(stage_slug)

    # to validate, that the link was parsed correctly
    assert link == generate_question_link(competition_slug, stage, year, grade, part, number)

    competition = Competition.objects.get(slug=competition_slug)

    try:
        questions_batch =  Question.objects.filter(
            competition=competition,
            stage=stage,
            year=year,
            grade=grade,
            part=part
        )
    except Question.DoesNotExist:
        raise Http404('Question does not exist')

    try:
        if grade == 11:
            question =  questions_batch.filter(number_11=number)
        elif grade == 10:
            question = questions_batch.filter(number_10=number)
        elif grade == 9:
            question = questions_batch.filter(number_9=number)
        else:
            question = questions_batch.filter(number_others=number)
    except Question.DoesNotExist:
        raise Http404('Question does not exist')

    # check that the queryset has length 1
    if len(question) == 0:
        raise Http404('Question does not exist')
    elif len(question) > 1:
        raise Http404('Error in database: more than one question with the same number!')

    return question


# TODO Checking answers
# TODO Validating answers with related models


# === Below just a code I want to save ===

# from dataclasses import dataclass
# from os import stat
# from typing import Any, Sequence, Type

# from django.core.exceptions import ValidationError
# from django.db import transaction
# from django.db.models.query import QuerySet

# from .models import BaseQuestion
# from .configs import EVALUATE_THRASHHOLD

# class QuestionChangeService:
#     """Service used to upload and modify questions. Validation occurs here."""

#     def __init__(self, question: Type[BaseQuestion], related_models) -> None:
#         self.question = question
#         self.related_models = related_models
    
#     def _validate_type(self):
#         """To ensure, that type is correct and number of answers corresponds to this type"""

#         qtype = self.question.type

#         answers = self.question.right_answers.all()
#         print(f'GOT RELATED: {answers}')
#         print(qtype)

#         if qtype == 'REL':
#             if answers.exclude(flag__isnull=True).exists():
#                 raise ValidationError('Вопрос на соответствие не может иметь заполненные поля "выбор варианта"!')

#         if qtype == 'STR':
#             # transaction.savepoint_rollback(self._save_id)
#             raise ValidationError('Всё работает!')

#     def create(self) -> BaseQuestion:

#         # Save question to have an ability to add related models
#         # self._save_id = transaction.savepoint()
#         question = self.question
#         question.full_clean()
#         question.save()
#         print('QUESTION SAVED')
        
#         # Add and save related
#         for model_name, model in self.related_models.items():
#             for related_object in model:
#                 getattr(question, model_name).add(related_object)
#         print('RELATED ADDED')
#         question.save()
#         print('RELATED SAVED')
        
#         self._validate_type()
#         print('TYPES VALIDATED')

#         return question

#     def update(self) -> BaseQuestion:
#         raise NotImplementedError

# class QuestionService:

#     @staticmethod
#     def validate_type(question) -> None:
#         """To ensure, that type is correct and number of answers corresponds to this type"""

#         answers = question.right_answers.all()
#         qtype = question.type

#         raise ValidationError(f'{answers.count()}')

#         if qtype == 'REL':
#             for ans in answers:
#                 if ans.has_flag:
#                     raise ValidationError('Вопрос на соответствие не может иметь заполненные поля "выбор варианта"!')       


# @dataclass(frozen=True)
# class Message:
#     text: str
#     status: str

#     def __post_init__(self):
#         status_list = ('right', 'partial', 'wrong')
#         if self.status not in status_list:
#             raise ValueError(f'Wrong status "{self.status}"! It should be in {status_list}')

# def get_message(self) -> Message:
#     if self.user_points == self.max_points:
#         message = 'Верно'
#         status = 'right'
#     elif self.user_points / self.max_points > EVALUATE_THRASHHOLD:
#         message = 'Частично верно. Есть куда стремится :)'
#         status = 'partial'
#     else:
#         message = 'Совсем мало правильных ответов :( Ботайте, и всё обязательно получится!'
#         status = 'wrong'
#     return message, status