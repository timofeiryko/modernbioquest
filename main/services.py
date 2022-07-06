"""Custom classes and functions for domain logic (aka business logic).
Most of this logic is related with objects, data stuctures etc.
The `scripts.py` is the other place where domain logic is placed (just some tools, not related with particular abstractions at all)."""

from dataclasses import dataclass
from os import stat
from typing import Type

from django.forms import ValidationError
from django.db import transaction

from .models import BaseQuestion
from .configs import EVALUATE_THRASHHOLD



# class QuestionChange:
#     """Service used to upload and modify questions. Validation occurs here."""

#     def __init__(self, question: Type[BaseQuestion]) -> None:
#         self.question = question
    
#     def _validate_type(self):
#         """To ensure, that type is correct and number of answers corresponds to this type"""

#         answers = self.question.right_answers.all()
#         qtype = self.question.type

#         if qtype == 'REL':
#             if answers.exclude(flag__isnull=True).exists():
#                 raise ValidationError('Вопрос на соответствие не может иметь заполненные поля "выбор варианта"!')

#     @transaction.atomic
#     def create(self) -> BaseQuestion:

#         self._validate_type()

#         file_name, file_type = self._infer_file_name_and_type(file_name, file_type)

#         obj = File(
#             file=self.file_obj,
#             original_file_name=file_name,
#             file_name=file_generate_name(file_name),
#             file_type=file_type,
#             uploaded_by=self.user,
#             upload_finished_at=timezone.now()
#         )

#         obj.full_clean()
#         obj.save()

#         return obj

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