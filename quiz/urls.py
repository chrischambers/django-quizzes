from django.conf.urls.defaults import *
from quiz.models import Quiz
from quiz import views
from django.views.generic import list_detail

data = {
    'queryset': Quiz.objects.filter(status=Quiz.LIVE),
}

urlpatterns = patterns('',
    url(r'^$', list_detail.object_list, data, name='quiz_list'),
    url(r'^(?P<slug>[^/]+)/$', views.quiz_detail, name='quiz_detail'),
    url(r'^(?P<slug>[^/]+)/complete/(?P<pk>\d+)/$',
        views.quiz_completed, name='quiz_completed'),
)
