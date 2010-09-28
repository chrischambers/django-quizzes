from django.db import models
from django.db.models import Sum
from django.db.models.query import QuerySet


class DRYManager(models.Manager):
    """Will try and use the queryset's methods if it cannot find
    its own. This allows you to define your custom filtering/exclusion
    methods in one place only (i.e., a custom QuerySet).

    Excerpted from:
    http://stackoverflow.com/questions/2163151/custom-queryset-and-manager-without-breaking-dry
    """
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


class AnswerQuerySet(QuerySet):
    @property
    def score(self):
        """Returns integer - total score of answers in queryset."""
        return self.aggregate(Sum('score')).values()[0] or 0

    @property
    def correct(self):
        from quiz.models import Answer
        return self.filter(score=Answer.CORRECT)

    @property
    def incorrect(self):
        from quiz.models import Answer
        return self.filter(score=Answer.INCORRECT)


class AnswerManager(DRYManager):
    use_for_related_fields = True

    def get_query_set(self):
        return AnswerQuerySet(self.model)
