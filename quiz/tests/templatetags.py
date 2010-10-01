from nose.tools import *

from django.contrib.auth.models import User
from django.test import TestCase
from quiz.models import Quiz, QuizResult

from quiz.templatetags.quiz_tags import percentage, quiz_taken


class TestPercentageFilter(TestCase):
    def test_percentage_filter(self):
        data = (
            (10,  100, 10.0),
            (5,   100, 5.0),
            (100, 100, 100.0),
            (1,   100, 1.0),
            (10,  200, 5.0),
            (200, 100, 200),
            (10,  0,   ''),
            ('',  100, ''),
            (10,  '',  ''),
        )

        for part, population, expected in data:
            assert_equal(expected, percentage(part, population))


class TestQuizTakenFilter(TestCase):
    fixtures = ['python-zen.yaml', 'testuser.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)
    # A single test-user, TestyMcTesterson, with password 'password'

    def setUp(self):
        super(TestQuizTakenFilter, self).setUp()
        self.quiz = Quiz.objects.get(slug='python-zen')
        self.user = User.objects.get(username='TestyMcTesterson')

    def test_quiz_taken_with_valid_inputs(self):
        assert_equal(0, quiz_taken(self.user, self.quiz))
        result = QuizResult.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=9,
            maximum_score=9
        )
        assert_equal(1, quiz_taken(self.user, self.quiz))
        result2 = QuizResult.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=8,
            maximum_score=9
        )
        assert_equal(2, quiz_taken(self.user, self.quiz))
        result.delete()
        assert_equal(1, quiz_taken(self.user, self.quiz))
        result2.delete()
        assert_equal(0, quiz_taken(self.user, self.quiz))

    def test_quiz_taken_with_invalid_inputs(self):
        assert_equal('', quiz_taken('foo', self.quiz))
        assert_equal('', quiz_taken(self.user, 'foo'))
        assert_equal('', quiz_taken(1, 2))

