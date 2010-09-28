from django.test import TestCase
from quiz.models import Question, Answer
from nose.tools import *


class TestAnswerQueryset(TestCase):
    fixtures = ['python-zen.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)

    def test_score_property(self):
        assert_equal(Question.objects.count(), Answer.objects.score)
        q = Question.objects.create(question='the new answer count should be...')
        a = Answer.objects.create(question=q, answer='10', score=Answer.CORRECT)
        assert_equal(10, Answer.objects.score)
        a = Answer.objects.create(question=q, answer='Incorrect')
        assert_equal(10, Answer.objects.score)
        Answer.objects.all().delete()
        assert_equal(0, Answer.objects.score)

    def test_correct_property(self):
        correct_answers = Answer.objects.filter(score=Answer.CORRECT)
        assert_equal(list(correct_answers), list(Answer.objects.correct))

    def test_incorrect_property(self):
        incorrect_answers = Answer.objects.filter(score=Answer.INCORRECT)
        assert_equal(list(incorrect_answers), list(Answer.objects.incorrect))

    def test_correct_incorrect_membership(self):
        q = Question.objects.create(question='Test question')
        a1 = Answer.objects.create(question=q, answer='f')
        a2 = Answer.objects.create(question=q, answer='t', score=Answer.CORRECT)
        assert a1 in Answer.objects.incorrect
        assert a1 not in Answer.objects.correct
        assert a2 not in Answer.objects.incorrect
        assert a2 in Answer.objects.correct
