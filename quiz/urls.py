from django.conf.urls.defaults import *
from quiz.models import Quiz
from django.views.generic import list_detail

data = {
    'queryset': Quiz.objects.filter(status=Quiz.LIVE),
}

urlpatterns = patterns('',
    url(r'^$', list_detail.object_list, data, name='quiz_list'),
)
