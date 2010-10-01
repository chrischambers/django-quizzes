import re
from nose.tools import *

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from quiz.forms import EmailForm
from quiz.models import Quiz, QuizResult


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


class TestQuizDetailView(TestCase):
    fixtures = ['python-zen.yaml', 'testuser.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)
    # A single test-user, TestyMcTesterson, with password 'password'

    input_re = re.compile('name="([^"]+)" value="([^"]+)"')

    def setUp(self):
        super(TestQuizDetailView, self).setUp()
        self.quiz = Quiz.objects.get(slug='python-zen')
        self.user = User.objects.get(username='TestyMcTesterson')

        self.data = ({
                'wizard_step': '0',
                '0-INITIAL_FORMS': 4,
                '0-TOTAL_FORMS': 4,
                '0-0-answers': 3,
                '0-1-answers': 4,
                '0-2-answers': 9,
                '0-3-answers': 11,
            }, {
                'wizard_step': '1',
                '1-INITIAL_FORMS': 3,
                '1-TOTAL_FORMS': 3,
                '1-0-answers': 14,
                '1-1-answers': 16,
                '1-2-answers': 20
            }, {
                'wizard_step': '2',
                '2-INITIAL_FORMS': 2,
                '2-TOTAL_FORMS': 2,
                '2-0-answers': 23,
                '2-1-answers': 26,
            }
        )

    def grab_field_data(self, response):
        """
        Pulls the appropriate field data from the context to pass to the next
        wizard step.

        -- Excerpted (but modified) from actual Django Formwizard tests
        """
        previous_fields = "".join([
            f.as_text() for f in response.context['previous_fields']
        ])
        fields = {'wizard_step': response.context['step0']}

        def grab(m):
            fields[m.group(1)] = m.group(2)
            return ''

        self.input_re.sub(grab, previous_fields)
        return fields

    def complete_quiz(self, slug):
        response = self.client.post(
            reverse('quiz_detail', args=[slug]), data=self.data[0]
        )
        assert_equal(200, response.status_code)
        data = self.grab_field_data(response)
        data.update(self.data[1])
        response = self.client.post(
            reverse('quiz_detail', args=[slug]), data=data
        )
        data = self.grab_field_data(response)
        data.update(self.data[2])
        response = self.client.post(
            reverse('quiz_detail', args=[slug]), data=data
        )
        return response

    def test_quiz_detail_view_with_no_inputs(self):
        response = self.client.get(
            reverse('quiz_detail', args=[self.quiz.slug]), follow=True
        )
        assert_equal(200, response.status_code)

    def test_quiz_detail_view_with_good_inputs_authenticated(self):
        self.assertTrue(
            self.client.login(username=self.user.username, password='password')
        )
        assert_false(QuizResult.objects.count())
        response = self.complete_quiz(self.quiz.slug)
        quiz_result = QuizResult.objects.get(
            quiz=self.quiz, user=self.user
        )
        self.assertRedirects(
            response,
            reverse('quiz_completed', args=(self.quiz.slug, quiz_result.pk)),
            status_code=302,
            target_status_code=200
        )
        assert_equal(self.user.email, quiz_result.email)
        assert_equal(quiz_result.score, self.quiz.questions.answers.maximum_score)
        assert_equal(quiz_result.score, quiz_result.maximum_score)
        assert_equal(
            set(quiz_result.answers.all()), set(self.quiz.questions.answers.correct)
        )

    def test_quiz_detail_redirects_for_anon_users_with_no_session_email(self):
        response = self.client.get(
            reverse('quiz_detail', args=(self.quiz.slug,)), follow=True
        )
        expected_redirect = "%s?next=%s" % (
            reverse('quiz_capture_email'),
            reverse('quiz_detail', args=(self.quiz.slug,))
        )
        self.assertRedirects(response, expected_redirect)

    def test_quiz_detail_view_with_good_inputs_unauthenticated(self):
        assert_false(QuizResult.objects.count())

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Waiting for this to land... http://code.djangoproject.com/ticket/10899
        # What SHOULD be as simple as this:
        # >>> self.client.session['email'] = 'foo@bar.com'
        # is currently this madness...
        from django.conf import settings
        from django.utils.importlib import import_module
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()  # we need to make load() work, or the cookie is worthless
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        session = self.client.session
        session['email'] = 'foo@bar.com'
        session.save()
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        response = self.complete_quiz(self.quiz.slug)
        quiz_result = QuizResult.objects.get(
            quiz=self.quiz, email='foo@bar.com'
        )
        self.assertRedirects(
            response,
            reverse('quiz_completed', args=(self.quiz.slug, quiz_result.pk)),
            status_code=302,
            target_status_code=200
        )
        assert not quiz_result.user
        assert_equal(quiz_result.score, self.quiz.questions.answers.maximum_score)
        assert_equal(quiz_result.score, quiz_result.maximum_score)
        assert_equal(
            set(quiz_result.answers.all()), set(self.quiz.questions.answers.correct)
        )

    def test_quiz_detail_for_draft_quiz_displays(self):
        self.quiz.status = Quiz.DRAFT
        self.quiz.save()
        response = self.client.get(self.quiz.get_absolute_url(), follow=True)
        assert_equal(200, response.status_code)

    def test_quiz_detail_for_closed_quiz_not_found(self):
        self.quiz.status = Quiz.CLOSED
        self.quiz.save()
        response = self.client.get(self.quiz.get_absolute_url(), follow=True)
        assert_equal(404, response.status_code)


class TestQuizCaptureEmailView(TestCase):
    fixtures = ['python-zen.yaml', 'testuser.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)
    # A single test-user, TestyMcTesterson, with password 'password'

    def setUp(self):
        super(TestQuizCaptureEmailView, self).setUp()
        self.quiz = Quiz.objects.get(slug='python-zen')
        self.user = User.objects.get(username='TestyMcTesterson')

    def test_authenticated_users_redirected_to_quiz_list(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('quiz_capture_email'), follow=True)
        self.assertRedirects(response, reverse('quiz_list'))

    def test_unauthenticated_users_not_redirected(self):
        response = self.client.get(reverse('quiz_capture_email'), follow=True)
        assert_equal(200, response.status_code)

    def test_emailform_success(self):
        data = {'email': 'foo@bar.com'}
        response = self.client.post(
            reverse('quiz_capture_email'), data=data, follow=True
        )
        self.assertRedirects(response, reverse('quiz_list'))
        assert_equal(data['email'], response.client.session['email'])
        response = self.client.get(
            reverse('quiz_detail', args=(self.quiz.slug,)), follow=True
        )
        assert_equal(200, response.status_code)

    def test_emailform_with_existing_user_email(self):
        response = self.client.post(
            reverse('quiz_capture_email'), {'email': self.user.email}, follow=True
        )
        self.assertFormError(
            response, 'form', 'email', EmailForm.EXISTING_EMAIL_ADDRESS
        )
