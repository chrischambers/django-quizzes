from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import simple

from quiz.models import Quiz, Question, QuizResult
from quiz.forms import quiz_formset_factory, QuizBoundFormWizard, EmailForm
try:
    from functools import partial
except ImportError: # Python 2.3, 2.4 fallback.
    from django.utils.functional import curry as partial

def redirect_to_quiz_list(request, *args, **kwargs):
    return simple.redirect_to(request, url=reverse('quiz_list'))

def capture_email(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('quiz_list'))
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            next = request.GET.get('next') or reverse('quiz_list')
            return HttpResponseRedirect(next)
    else:
        form = EmailForm()

    data = {'form': form, }

    return render_to_response("quiz/capture_email.html", data,
                            context_instance=RequestContext(request))

def quiz_detail(request, slug, *args, **kwargs):
    quiz = get_object_or_404(Quiz.objects.exclude(status=Quiz.CLOSED), slug=slug)
    if not request.user.is_authenticated() and not request.session.get('email'):
        redirect_url = "%s?next=%s" % (
            reverse('quiz_capture_email'), request.path
        )
        return HttpResponseRedirect(redirect_url)
    FormSet = quiz_formset_factory(quiz)
    easy    = partial(FormSet, difficulty=Question.EASY,   prefix='easy')
    medium  = partial(FormSet, difficulty=Question.MEDIUM, prefix='medium')
    hard    = partial(FormSet, difficulty=Question.HARD,   prefix='hard')
    extra_context = {'quiz': quiz}
    return QuizBoundFormWizard([easy, medium, hard])(
        request, extra_context=extra_context, *args, **kwargs
    )

def quiz_completed(request, slug, pk, *args, **kwargs):
    results = get_object_or_404(QuizResult.objects.select_related(
        'quiz', 'user').filter(quiz__slug=slug), pk=pk
    )
    data = {
         'results':        results,
         'quiz':           results.quiz,
         'test_taker':     results.user,
         'score':          results.score,
         'maximum_score':  results.maximum_score,
         'datetime_taken': results.datetime_created
    }
    return render_to_response("quiz/quiz_complete.html", data,
                        context_instance=RequestContext(request))

