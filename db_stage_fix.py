"""My one-time utility to restore stage from db_pickles and update the database."""

import os, sys
import pickle
import logging

import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bioquest.settings')
django.setup()

from main.models import Question, NewStage
from pdfparsing.parser_dataclasses import QuestionDraft, CleanedQuestion
from to_db_uploader import load_data

REG_DUMP_FILENAMES = ['reg_parts_1-2_2018.p',  'reg_parts_1-2_2019.p',  'reg_parts_1-2_2020.p',  'reg_parts_1-2_2021.p']

# logging to console
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def main():

    all_questions = Question.objects.all()
    reg_stage = NewStage.objects.get(name='Региональный')

    for filename in REG_DUMP_FILENAMES:
        cleaned_questions = load_data(filename, logger)

        for cleaned_question in cleaned_questions.values():

            text = cleaned_question.text
            # find this question in the database
            question = all_questions.filter(text=text)

            if len(question) > 1:
                logger.warning('Multiple questions found!')
                for single_question in question:
                    logger.info(single_question.text)
                    logger.info(single_question.year)
                continue
            elif len(question) == 0:
                continue

            # update stage
            question = question.first()
            question.new_stage = reg_stage
            question.save()
            

if __name__ == '__main__':
    main()