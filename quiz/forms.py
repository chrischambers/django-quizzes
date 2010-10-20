from django import forms
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory, BaseFormSet, INITIAL_FORM_COUNT
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from quiz.models import Answer, QuizResult
from wadofstuff.django.forms import BoundFormWizard


class EmailForm(forms.Form):
    """Simple form for capturing an unauthenticated user's email address."""

    EXISTING_EMAIL_ADDRESS = _(
        'This email address already belongs to a user '
        'on our site.'
    )
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(self.EXISTING_EMAIL_ADDRESS)
        return email


class QuestionForm(forms.Form):
    answers = forms.TypedChoiceField(
        widget=forms.RadioSelect(),
        coerce=int,
        label=_("Please select an answer:")
    )

    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.question = question.question
        answers = question.answers.live
        self.fields['answers'].choices = question.answers.values_list('pk', 'answer')

    @property
    def score(self):
        if not self.is_valid():
            return False

        return self.cleaned_data['answers'].score

    def is_correct(self):
        return self.score >= 1


class QuizBaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        for var in ['quiz', 'difficulty']:
            val = kwargs.pop(var, None)
            if val:
                setattr(self, var, val)
        super(QuizBaseFormSet, self).__init__(*args, **kwargs)

    def initial_form_count(self):
        """Returns the number of forms that are required in this FormSet."""
        if self.data or self.files:
            return self.management_form.cleaned_data[INITIAL_FORM_COUNT]
        else:
            questions = self.quiz.questions.live
            if hasattr(self, 'difficulty'):
                questions = questions.filter(difficulty=self.difficulty)
            return questions.count()

    def _construct_forms(self):
        # TODO: Find cleaner way of making this happen.
        self.forms = []
        questions = self.quiz.questions.live.order_by('id')
        if hasattr(self, 'difficulty'):
            questions = questions.filter(difficulty=self.difficulty)
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i, question=questions[i]))

    def get_answers(self):
        if self.is_valid():
            answer_ids = [f.cleaned_data['answers'] for f in self.forms]
            answers = Answer.objects.filter(id__in=answer_ids)
            return answers

    def calculate_score(self):
        answers = self.get_answers()
        self.result = answers.score
        return self.result

    @property
    def maximum_score(self):
        questions = self.quiz.questions.live
        if hasattr(self, 'difficulty'):
            questions = questions.filter(difficulty=self.difficulty)
        relevant_answers = Answer.objects.filter(question__in=questions)
        return relevant_answers.maximum_score

    def calculate_score_percentage(self, round=True):
        if not round:
            round = lambda x: x
        if not hasattr(self, 'result'):
            self.calculate_score()
        return int(round((float(self.result) / self.maximum_score) * 100))


def quiz_formset_factory(quiz, form=QuestionForm, formset=QuizBaseFormSet,
                         extra=0, *args, **kwargs):
    # NOTE: force extra set to 0, as otherwise you'll raise an IndexError.
    extra = 0
    formset = formset_factory(form, formset, extra, *args, **kwargs)
    formset.quiz = quiz
    return formset


class QuizBoundFormWizard(BoundFormWizard):
    # The BoundFormWizard parent is necessary because the default FormWizard
    # doesn't handle formsets.

    def get_template(self, step):
        return 'quiz/wizard.html'

    def get_total_score(self, formset_list):
        return sum(formset.calculate_score() for formset in formset_list)

    def get_maximum_score(self, formset_list):
        return sum(formset.maximum_score for formset in formset_list)

    def done(self, request, formset_list):
        quiz      = formset_list[0].quiz
        score     = self.get_total_score(formset_list)
        max_score = self.get_maximum_score(formset_list)
        answers   = reduce(lambda x,y: x|y, (fs.get_answers() for fs in formset_list))
        if request.user.is_authenticated():
            data = {'user': request.user, 'email': request.user.email}
        else:
            data = {'email': request.session['email']}
        result = QuizResult.objects.create(
            quiz=quiz,
            score=score,
            maximum_score=max_score,
            **data
        )
        result.answers.add(*answers)
        return HttpResponseRedirect(result.get_absolute_url())
