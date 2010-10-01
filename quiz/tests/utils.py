from nose.tools import *
from unittest import TestCase
from quiz.models import Question
from quiz.utils import get_display_name

class TestGetDisplayName(TestCase):

    def test_get_display_name(self):
        mapping = (
            ( Question.DIFFICULTY_CHOICES[0][0],
              Question.DIFFICULTY_CHOICES[0][1], ),
            ( Question.DIFFICULTY_CHOICES[1][0],
              Question.DIFFICULTY_CHOICES[1][1], ),
            ( Question.DIFFICULTY_CHOICES[2][0],
              Question.DIFFICULTY_CHOICES[2][1], ),
        )
        for inp, expected in mapping:
            assert_equal(get_display_name(inp), expected)
