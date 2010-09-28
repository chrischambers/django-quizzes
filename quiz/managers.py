from django.db import models
from django.db.models import Count, Sum, Max
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
    def maximum_score(self):
        """Returns the maximum score possible for a given set of answers."""
        max_score = self.values('question').annotate(
            top_answer=Max('score')
        )
        max_score = sum(d['top_answer'] for d in max_score)
        return max_score

    @property
    def correct(self):
        from quiz.models import Answer
        return self.filter(score=Answer.CORRECT)

    @property
    def incorrect(self):
        from quiz.models import Answer
        return self.filter(score=Answer.INCORRECT)


class QuestionQuerySet(QuerySet):
    @property
    def answers(self):
        """Returns the answers for a given question set."""
        from quiz.models import Answer
        qids = self.values_list('id', flat=True)
        return Answer.objects.filter(
            question__id__in=qids).select_related('question')

    @property
    def total_answers(self):
        """Returns a count of the total answers for a given question set."""
        return self.select_related('answers').annotate(
                answer_count=Count('answers')
                ).aggregate(Sum('answer_count')).values()[0] or 0


class AnswerManager(DRYManager):
    use_for_related_fields = True

    def get_query_set(self):
        return AnswerQuerySet(self.model)


class QuestionManager(DRYManager):
    use_for_related_fields = True

    def get_query_set(self):
        return QuestionQuerySet(self.model)
