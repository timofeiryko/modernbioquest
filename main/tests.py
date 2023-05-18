from django.test import TestCase

from main.models import Question, RightAnswer, User, SolvedQuestion, UserAnswer, Competition, NewStage
from main.services import check_user_answers_P1


class TestCheckUserAnswers(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='password'
        )

        # Create a question with 4 variants
        self.question = Question.objects.create(
            text='What is the capital of France?',
            type='P1',
            quauthor=self.user,
            competition=Competition.objects.all().first(),
            new_stage=NewStage.objects.filter(competition=Competition.objects.all().first()).first(),
            year=2021,
            grade=13,
            number_9=0,
            number_10=0,
            number_11=1,
            number_others=0
        )

        RightAnswer.objects.create(
            parent_question=self.question,
            label='Paris',
            flag=True
        )

        RightAnswer.objects.create(
            parent_question=self.question,
            label='London',
            flag=False
        )

        RightAnswer.objects.create(
            parent_question=self.question,
            label='Berlin',
            flag=False
        )

        RightAnswer.objects.create(
            parent_question=self.question,
            label='New York',
            flag=False
        )

    def test_check_user_answers_P1(self):

        # Test with correct answer

        user_answer = 'Paris'
        right_answers, user_answers, solved_question = check_user_answers_P1(self.question, self.user, user_answer)
        
        # Test that user answers objects a created correctly
        self.assertEqual(len(user_answers), 4)
        self.assertEqual(user_answers[0].label, 'Paris')
        self.assertEqual(user_answers[1].label, 'London')

        # Test that solved question object is created correctly
        self.assertEqual(solved_question.solved_by, self.user)
        self.assertEqual(solved_question.parent_question, self.question)

        # print all solved questions params
        for param in solved_question.__dict__:
            print(param, solved_question.__dict__[param])

        # print all user answers
        for user_answer in UserAnswer.objects.filter(parent_solved=solved_question):
            print(user_answer.label, user_answer.flag)


        # Ensure that points and score are calculated correctly
        self.assertEqual(solved_question.user_points, 1)
        self.assertEqual(solved_question.user_score, 1)

        # Test with incorrect answer

        user_answer = 'London'
        right_answers, user_answers, solved_question = check_user_answers_P1(self.question, self.user, user_answer)

        # print all solved questions params
        for param in solved_question.__dict__:
            print(param, solved_question.__dict__[param])

        # print all user answers
        for user_answer in UserAnswer.objects.filter(parent_solved=solved_question):
            print(user_answer.label, user_answer.flag)

        # Ensure that points and score are calculated correctly
        self.assertEqual(solved_question.user_points, 0)
        self.assertEqual(solved_question.user_score, 0)

