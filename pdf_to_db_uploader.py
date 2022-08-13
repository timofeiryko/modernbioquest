"""My utility to upload VsOSh questions to the databaes from pickle files, generated by pdfparsing module"""

# TODO CLI instead of constants in code
import os, sys
import pickle
import logging
from datetime import datetime, date

import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bioquest.settings')
django.setup()

from main.models import Competition, Explanation, Section, Topic, Question, RightAnswer, User
import pdfparsing.parser_dataclasses
from main.scripts import get_max_score_zakl, generate_question_link

logging.basicConfig(filename=f'parsing-{date.today()}.log', level=logging.DEBUG)

# Better to parse args from terminal, but I am lazy and I will just modify this code file
P2_SCALE = 'LATEST_ZAKL_P2'
P3_SCALE = 'LATEST_ZAKL_P3'
COMPETITION_NAME = 'ВсОШ'
STAGE = 'Заключительный'
GRADE = 11

def get_type_2022(part: int) -> str:
    if part == 1:
        return 'P1'
    elif part == 2 or part == 3:
        return 'P2'
    elif part == 4:
        return 'REL'
    elif part == 5:
        return 'STR'

def load_data():
    
    logging.info('LOADING DATA FROM PICKLE...')

    sys.modules['parser_dataclasses'] = pdfparsing.parser_dataclasses
    cleaned_questions = pickle.load(open(os.path.join('main', 'db_pickles', FILENAME), 'rb'))

    logging.info('EXAMPLE DATA:')
    logging.info(cleaned_questions[4, 3].text)
    del sys.modules['parser_dataclasses']

    logging.info('DATA LOADED!')

    return cleaned_questions

@transaction.atomic
def upload_questions(cleaned_questions):

    ids = []

    for input_question in cleaned_questions.values():

        part = input_question.question.part

        user = User.objects.get(username='parser')
        competition = Competition.objects.get(name=COMPETITION_NAME)

        question = Question(

            text = input_question.text,
            max_score = get_max_score_zakl(part, P2_SCALE, P3_SCALE),
            quauthor = user,
            type = get_type_2022(part),
            listed = False,

            competition = competition,
            year = YEAR,
            stage = STAGE,
            grade = GRADE,
            part = part,
            number_11 = input_question.question.number
        )

        if input_question.question.title:
            question.title = input_question.question.title

        question.save()

        ids.append(question.id)
    
    logging.info(f'{len(cleaned_questions)} QUESTIONS UPLOADED!')

    return ids

@transaction.atomic
def upload_related(cleaned_questions, ids):
    for input_question, id in zip(cleaned_questions.values(), ids):
        
        question = Question.objects.get(id=id)

        for answer_variant in input_question.answer_variants:


            right_answer = RightAnswer(label = answer_variant, parent_question = question)
            
            # ATTENTION! May be not always right way to fill
            if str(question.type) in ['P1', 'P2']:
                right_answer.flag = False
                right_answer.save()

            right_answer.save()

        if not input_question.answer_variants:
            logging.warning(f'NO VARIANTS FOR QUESTION {question.id}({question.link})')


def main():

    global FILENAME
    global YEAR

    for upload_iter in [2019, 2021, 2022]:
        YEAR = upload_iter
        FILENAME = f'zakl{YEAR}.p'
        logging.info(f'UPLOADING YEAR {YEAR}...')

        cleaned_questions = load_data()
        ids = upload_questions(cleaned_questions)
        upload_related(cleaned_questions, ids)

        logging.info(f'UPLOADED YEAR {YEAR}!')
    
def remove_uploaded():
    Question.objects.filter(quauthor__username = 'parser').filter(year__in=[2019, 2021, 2022]).delete()

if __name__ == '__main__':
    remove_uploaded()