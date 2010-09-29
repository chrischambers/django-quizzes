from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from quiz.models import Quiz, Question, QuizResult
from quiz.forms import quiz_formset_factory, QuizBoundFormWizard
try:
    from functools import partial
except ImportError: # Python 2.3, 2.4 fallback.
    from django.utils.functional import curry as partial

def quiz_detail(request, slug, *args, **kwargs):
    quiz    = get_object_or_404(Quiz, slug=slug)
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

