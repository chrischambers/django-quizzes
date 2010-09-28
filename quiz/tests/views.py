from django.test import TestCase
from django.core.urlresolvers import reverse
from quiz.models import Quiz

class TestQuizListView(TestCase):
    fixtures = ['python-zen.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)

    def setUp(self):
        super(TestQuizListView, self).setUp()
        self.quiz = Quiz.objects.get(slug='python-zen')

    def test_quiz_list_view_with_single_live_quiz(self):
        response = self.client.get(reverse('quiz_list'), follow=True)
        self.assertContains(response, self.quiz.name, count=1, status_code=200)
        self.assertContains(response, self.quiz.description, count=1)

    def test_quiz_list_view_with_single_draft_quiz(self):
        self.quiz.status=Quiz.DRAFT
        self.quiz.save()
        response = self.client.get(reverse('quiz_list'), follow=True)
        self.assertNotContains(response, self.quiz.name, status_code=200)
        self.assertNotContains(response, self.quiz.description)

    def test_quiz_list_view_with_single_closed_quiz(self):
        self.quiz.status=Quiz.CLOSED
        self.quiz.save()
        response = self.client.get(reverse('quiz_list'), follow=True)
        self.assertNotContains(response, self.quiz.name, status_code=200)
        self.assertNotContains(response, self.quiz.description)

    def test_quiz_list_view_with_two_live_quizzes(self):
        q2 = Quiz.objects.create(
            name='Test Quiz 2',
            slug='test-quiz-2',
            description='Foobar',
            status=Quiz.LIVE
        )
        response = self.client.get(reverse('quiz_list'), follow=True)
        self.assertContains(response, self.quiz.name, count=1, status_code=200)
        self.assertContains(response, self.quiz.description, count=1)
        self.assertContains(response, q2.name, count=1, status_code=200)
        self.assertContains(response, q2.description, count=1)
