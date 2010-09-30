from django.contrib.auth.models import User
from django.test import TestCase
from nose.tools import *

from quiz.models import QuizResult, Quiz
from quiz.listeners import start_listening, stop_listening

class TestUpdateQuizResultsSignal(TestCase):
    """Signal connections persist across tests, so we need to explicitly
    deactivate our signals."""

    fixtures = ['python-zen.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)

    def setUp(self):
        super(TestUpdateQuizResultsSignal, self).setUp()
        self.email = 'foo@bar.com'
        self.quiz = Quiz.objects.get(slug='python-zen')
        self.quiz_results = (
            QuizResult.objects.create(
                quiz=self.quiz,
                email=self.email,
                score=9,
                maximum_score=9,
            ),
            QuizResult.objects.create(
                quiz=self.quiz,
                email=self.email,
                score=9,
                maximum_score=9,
            ),
        )

    def tearDown(self):
        super(TestUpdateQuizResultsSignal, self).tearDown()
        stop_listening()

    def test_not_fired_without_signal_activated(self):
        u = User.objects.create(username='foo', email=self.email)
        assert not QuizResult.objects.filter(user=u)

    def test_fired_with_signal_activated(self):
        start_listening()
        u = User.objects.create(username='foo', email=self.email)
        assert_equal(
            set(QuizResult.objects.all()),
            set(QuizResult.objects.filter(user=u))
        )

        u2 = User.objects.create(username='bar', email=self.email)
        u3 = User.objects.create(username='baz', email='something@else.com')
        assert not QuizResult.objects.filter(user=u2)
        assert not QuizResult.objects.filter(user=u3)
