from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField
)
from threaded_multihost.fields import CreatorField, EditorField

from quiz.managers import QuestionManager, AnswerManager


class AuditedModel(models.Model):
    datetime_created = CreationDateTimeField(_('Created'))
    datetime_modified = ModificationDateTimeField(_('Last Modified'))


    class Meta(object):
        abstract = True


class Question(AuditedModel):
    EASY, MEDIUM, HARD = 1, 10, 20
    DIFFICULTY_CHOICES = (
        (EASY,   _('Easy')),
        (MEDIUM, _('Medium')),
        (HARD,   _('Hard')),
    )

    question = models.TextField(_('question'))
    difficulty = models.SmallIntegerField(_('difficulty'),
        default=EASY,
        choices=DIFFICULTY_CHOICES
    )
    is_active = models.BooleanField(_('is active'), default=True)


    # Metadata
    creator = CreatorField(
        verbose_name=_('creator'),
        related_name='questions_created',
        limit_choices_to={'is_staff': True}
    )
    editor  = EditorField(
        verbose_name=_('editor'),
        related_name='questions_last_modified',
        limit_choices_to={'is_staff': True}
    )

    objects = QuestionManager()


    class Meta(object):
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        get_latest_by = 'datetime_created'

    def __unicode__(self):
        return u"%s" % (self.question,)


class Answer(AuditedModel):
    """Represents a Multiple Choice Quiz Answer."""
    INCORRECT, CORRECT = 0, 1
    SCORE_CHOICES = (
        (INCORRECT, _('Incorrect')),
        (CORRECT,   _('Correct')),
    )

    question = models.ForeignKey(
        Question, verbose_name=_('question'), related_name='answers'
    )
    answer = models.TextField(_('answer'))
    score = models.SmallIntegerField(_('score'),
        default=INCORRECT,
        choices=SCORE_CHOICES
    )
    is_active = models.BooleanField(_('is active'), default=True)

    # Metadata
    creator = CreatorField(
        verbose_name=_('creator'),
        related_name='answers_created',
        limit_choices_to={'is_staff': True}
    )
    editor  = EditorField(
        verbose_name=_('editor'),
        related_name='answers_last_modified',
        limit_choices_to={'is_staff': True}
    )

    objects = AnswerManager()


    class Meta(object):
        unique_together = (('question', 'answer'),)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        get_latest_by = 'datetime_created'

    def __unicode__(self):
        return u"%s" % (self.answer,)


class Quiz(AuditedModel):
    LIVE, DRAFT, CLOSED = 1, 2, 3
    STATUS_CHOICES = (
        (LIVE,   _('Live')),
        (DRAFT,  _('Draft')),
        (CLOSED, _('Closed')),
    )

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)
    questions = models.ManyToManyField(Question, verbose_name=_('question'),
        null=True, blank=True, related_name='quizzes'
    )

    status = models.SmallIntegerField(
        _('status'), choices=STATUS_CHOICES, default=DRAFT
    )

    # Metadata:
    creator = CreatorField(
        verbose_name=_('creator'),
        related_name='quizzes_created',
        limit_choices_to={'is_staff': True}
    )
    editor  = EditorField(
        verbose_name=_('editor'),
        related_name='quizzes_last_modified',
        limit_choices_to={'is_staff': True}
    )


    class Meta(object):
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        get_latest_by = 'datetime_created'

    def __unicode__(self):
        return u"%s" % (self.name,)

    @models.permalink
    def get_absolute_url(self):
        return ('quiz_detail', [], {'slug': self.slug})


class QuizResult(AuditedModel):
    """Stores a snapshot of the quiz results for both users and
    unregistered users (unregistered users are identified by an
    email address)."""

    quiz = models.ForeignKey(Quiz, verbose_name=_('quiz'),
        related_name='results'
    )
    user = models.ForeignKey(User, verbose_name=_('user'),
        null=True, blank=True, related_name='quiz_results'
    )
    email = models.EmailField(_('email'), blank=True)

    answers = models.ManyToManyField(Answer, verbose_name=_('answers'),
        related_name='used', help_text=_(
            "The actual answers provided by the user. Note that if the "
            "answers/questions/quiz are modified after the user has taken "
            "the test these may not provide a true reflection of their "
            "actual responses."
    ))

    # Snapshot data:
    score = models.PositiveIntegerField(_('score'))
    maximum_score = models.PositiveIntegerField(_('maximum score'))

    # Metadata
    creator = CreatorField(
        verbose_name=_('creator'),
        related_name='quiz_results_created',
        limit_choices_to={'is_staff': True}
    )
    editor  = EditorField(
        verbose_name=_('editor'),
        related_name='quiz_results_last_modified',
        limit_choices_to={'is_staff': True}
    )

    class Meta(object):
        verbose_name = _('Quiz Result')
        verbose_name_plural = _('Quiz Results')
        get_latest_by = 'datetime_created'

    def __unicode__(self):
        username = self.user and self.user.username or self.email
        return u"%s - %s: (%s)" % (
            username, self.quiz,
            self.datetime_created.strftime('%d/%m/%Y, %H:%M:%S')
        )
