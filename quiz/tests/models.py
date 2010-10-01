from django.test import TestCase
from quiz.models import Question, Answer
from nose.tools import *


class TestQuestionAnswerStripWhiteSpace(TestCase):
    def setUp(self):
        super(TestQuestionAnswerStripWhiteSpace, self).setUp()
        self.expected = 'foo bar baz'
        self.variants = (
            '    foo bar baz',
            'foo bar baz    ',
            '  foo bar baz  ',
        )

    def test_question_strip_whitespace(self):
        for v in self.variants:
            question = Question.objects.create(
                question=v
            )
            assert_equal(question.question, self.expected)
            question.delete()

    def test_answer_strip_whitespace(self):
        question = Question.objects.create(question='foo')
        for v in self.variants:
            answer = Answer.objects.create(
                question=question,
                answer=v
            )
            assert_equal(answer.answer, self.expected)
            answer.delete()


class TestAnswerQueryset(TestCase):
    fixtures = ['python-zen.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)

    def test_live_property(self):
        assert_equal(Answer.objects.count(), Answer.objects.live.count())
        assert_equal(list(Answer.objects.all()), list(Answer.objects.live))
        assert_equal(
            list(Answer.objects.none()),
            list(Answer.objects.filter(id=None).live)
        )
        Answer.objects.update(is_active=False)
        assert_equal(0, Answer.objects.live.count())

    def test_score_property(self):
        assert_equal(Question.objects.count(), Answer.objects.score)
        q = Question.objects.create(question='the new answer count should be...')
        a = Answer.objects.create(question=q, answer='10', score=Answer.CORRECT)
        assert_equal(10, Answer.objects.score)
        a = Answer.objects.create(question=q, answer='Incorrect')
        assert_equal(10, Answer.objects.score)
        Answer.objects.all().delete()
        assert_equal(0, Answer.objects.score)

    def test_maximum_score_property(self):
        assert_equal(0, Answer.objects.filter(id=None).maximum_score)
        assert_equal(0, Answer.objects.incorrect.maximum_score)
        assert_equal(9, Answer.objects.correct.maximum_score)
        hard_questions = Question.objects.filter(
            difficulty=Question.HARD).values_list('id', flat=True)
        answers = Answer.objects.filter(question__id__in=hard_questions)
        assert_equal(hard_questions.count(), answers.maximum_score)

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


class TestQuestionQueryset(TestCase):
    fixtures = ['python-zen.yaml']
    # 1 quiz, 9 questions, 26 answers, 9 correct answers (one per question)

    def test_live_property(self):
        assert_equal(Question.objects.count(), Question.objects.live.count())
        assert_equal(list(Question.objects.all()), list(Question.objects.live))
        assert_equal(
            list(Question.objects.none()),
            list(Question.objects.filter(id=None).live)
        )
        Question.objects.update(is_active=False)
        assert_equal(0, Question.objects.live.count())

    def test_answers_property(self):
        assert_equal(
            list(Answer.objects.order_by('id')),
            list(Question.objects.answers.order_by('id'))
        )
        questions = Question.objects.all()[:5]
        expected  = [q.answers.all() for q in questions]
        expected  = sorted([i.id for sublist in expected for i in sublist])
        actual    = sorted([i.id for i in questions.answers])
        assert_equal(expected, actual)

    def test_total_answers_property(self):
        questions = Question.objects.all()
        assert_equal(questions.answers.count(), questions.total_answers)
        assert_equal(0, Question.objects.filter(id=None).total_answers)
