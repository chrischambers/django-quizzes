from nose.tools import *
from unittest import TestCase

from quiz.templatetags.quiz_tags import percentage


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

