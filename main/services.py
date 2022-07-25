"""Custom classes and functions for domain logic (aka business logic).
Most of this logic is related with objects, data stuctures etc.
The `scripts.py` is the other place where domain logic is placed (just some tools, not related with particular abstractions at all)."""



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