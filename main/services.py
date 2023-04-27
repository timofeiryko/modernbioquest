"""Custom classes and functions for domain logic (aka business logic).
Most of this logic is related with objects, data stuctures etc.
The `scripts.py` is the other place where domain logic is placed (just some tools, not related with particular abstractions at all)."""

from django.http import Http404
from django.db.models.query import QuerySet
from django.db.models import Q

from .models import Question, Competition, Section, Topic, NewStage
from .scripts import generate_question_link, get_stage_name, clean_query, fuzz_search
from .configs import FUZZ_TRESHOLD

from typing import List, Tuple, Optional

def extend_question_text(question: Question) -> str:
    """Extends question text with its title, answer variants, scetions and topics."""

    full_text = question.text
    
    full_text += question.verbose_title

    answer_variants = question.answer_variants()[0]
    for answer_variant in answer_variants:
        full_text += ('\n' + answer_variant.label if answer_variant.label else '' + ' ' + answer_variant.text if answer_variant.text else '')

    full_text += ('\n' + ' '.join([section.name for section in question.sections.all()]))
    full_text += ('\n' + ' '.join([topic.name for topic in question.topics.all()]))

    return full_text

def filter_questions_by_query(query: str, questions):
    """Returns questions by search query."""

    #TODO: SPEED IT UP

    # Check if query is a section name
    section = Section.objects.filter(name=query).first()
    if section:
        questions = get_questions_by_sections([section])
    
    # Check if query is a topic name
    topic = Topic.objects.filter(name=query).first()
    if topic:
        questions = Question.objects.order_by('-id').filter(listed = True, topics__name__icontains=topic.name)

    if not (section or topic):

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

    variant = None

    # link is defined by generate_question_link function from scripts.py
    link_parts = link.split('-')
    if len(link_parts) == 6:
        competition_slug, stage_slug, year, grade, part, number = link.split('-')
    elif len(link_parts) == 7:
        competition_slug, stage_slug, year, grade, part, variant, number = link.split('-')
    else:
        raise Http404('Question does not exist')
    
    competition = Competition.objects.get(slug=competition_slug)
    year, grade, part, number = int(year), int(grade), int(part), int(number)
    stage = NewStage.objects.get(slug=stage_slug, competition=competition)

    # to validate, that the link was parsed correctly
    correct_link = generate_question_link(competition_slug, stage_slug, year, grade, part, number, variant)
    assert link == correct_link, f'Link {link} is not valid, it shoud be {correct_link}!'
    print(link)
    print(variant)

    try:
        questions_batch =  Question.objects.filter(
            competition=competition,
            new_stage=stage,
            year=year,
            grade=grade,
            part=part
        )
    except Question.DoesNotExist:
        raise Http404('Question does not exist')
    
    if variant is not None:
        try:
            questions_batch = questions_batch.filter(variant=variant)
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

def advanced_filter_service(
        questions: QuerySet,
        requested_topics: Optional[List[str]],
        requested_sections: Optional[List[str]],

        requested_competitions: Optional[List[str]],
        requested_stages: Optional[List[str]],

        requested_years: Optional[List[str]],
        requested_parts: Optional[List[str]],
        requested_grades: Optional[List[str]]
) -> Tuple[QuerySet, str]:
    """Returns questions, filtered by all requested parameters."""

    

    p_content = ''

    if requested_sections is not None:
        
        if requested_topics:
            sections_without_topics = requested_sections.exclude(topics__name__in=requested_topics)
            sections_with_topics = requested_sections.filter(topics__name__in=requested_topics).distinct()
        else:
            sections_without_topics = requested_sections
            sections_with_topics = Section.objects.none()

        if sections_without_topics:
            p_content += f'Разделы целиком: <b>{", ".join([section.name for section in sections_without_topics])}</b><br>'
            questions_without_topics = questions.filter(sections__in=sections_without_topics)

        if requested_topics:

            questions  = questions.filter(topics__name__in=requested_topics)
            topics = Topic.objects.filter(name__in=requested_topics)

            # divide questions and topics into batches by section
            questions = [questions.filter(sections__in=[section]) for section in sections_with_topics]
            topics = [topics.filter(parent_section=section) for section in sections_with_topics]
            new_questions = []

            for section, topic_batch, question_batch in zip(sections_with_topics, topics, questions):
                new_questions.append(question_batch.filter(topics__in=topic_batch))
                p_content += f'<b>{section.name}</b>: {", ".join([topic.name for topic in topic_batch])}<br>'

            # merge batches into one queryset
            questions = Question.objects.none()
            for question_batch in new_questions:
                questions = questions | question_batch

            if sections_without_topics:
                questions = questions | questions_without_topics

        
    # TODO abstraction for similar filtering (competition + stage, section + topic)

    if requested_competitions:
        requested_competitions = Competition.objects.filter(slug__in=requested_competitions)

        if requested_stages:
            competitions_without_stages = requested_competitions.exclude(stages__slug__in=requested_stages)
            competitions_with_stages = requested_competitions.filter(stages__slug__in=requested_stages).distinct()
        else:
            competitions_without_stages = requested_competitions
            competitions_with_stages = Competition.objects.none()

        if competitions_without_stages:
            p_content += f'Олимпиады: <b>{", ".join([competition.name for competition in competitions_without_stages])}</b><br>'
            questions_without_stages = questions.filter(competition__in=competitions_without_stages)
            
        
        if requested_stages:

            questions = questions.filter(new_stage__slug__in=requested_stages)
            stages = NewStage.objects.filter(slug__in=requested_stages)

            # divide questions and stages into batches by competition
            questions = [questions.filter(competition=competition) for competition in competitions_with_stages]
            stages = [stages.filter(competition=competition) for competition in competitions_with_stages]
            new_questions = []

            for competition, stage_batch, question_batch in zip(competitions_with_stages, stages, questions):
                new_questions.append(question_batch.filter(new_stage__in=stage_batch))
                
                p_content += f'<b>{competition.name}</b>: {", ".join([stage.name for stage in stage_batch])}<br>'

            # merge batches into one queryset
            questions = Question.objects.none()
            for question_batch in new_questions:
                questions = questions | question_batch
            
            if competitions_without_stages:
                questions = questions | questions_without_stages

        else:
            
            questions = questions_without_stages

    if requested_years:
        questions = questions.filter(year__in=requested_years)
        p_content += f'Годы проведения: <b>{", ".join(requested_years)}</b><br>'
    
    if requested_parts:
        questions = questions.filter(part__in=requested_parts)
        p_content += f'Части: <b>{", ".join(requested_parts)}</b><br>'

    if requested_grades:
        # TODO Upgrade to Python 3.10 and use structural pattern matching

        # Filter, using number_9, number_10 and number_11 fields: if number_N is not 0 than the question is for N grade
        questions_9 = questions.filter(number_9__gt=0)
        questions_10 = questions.filter(number_10__gt=0)
        questions_11 = questions.filter(number_11__gt=0)

        # Merge questions_9, questions_10 and questions_11 into one queryset, according to requested_grades
        questions = Question.objects.none()
        if '9' in requested_grades:
            questions = questions | questions_9
        if '10' in requested_grades:
            questions = questions | questions_10
        if '11' in requested_grades:
            questions = questions | questions_11

        p_content += f'Классы: <b>{", ".join(requested_grades)}</b><br>'
    

    return questions, p_content


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
#         
#         

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
#         
        
#         # Add and save related
#         for model_name, model in self.related_models.items():
#             for related_object in model:
#                 getattr(question, model_name).add(related_object)
#         
#         question.save()
#         
        
#         self._validate_type()
#         

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