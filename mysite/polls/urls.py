from django.conf.urls import url

from . import views

app_name = 'polls'
urlpatterns = [
    # /
    url(
        r'^$',
        views.homepage,
        name='homepage'
    ),

    # /search/
    url(
        r'^search/$',
        views.search,
        name='search'
    ),
    # /1
    url(
        r'^(?P<voteresult_id>[0-9]+)/$',
        views.result,
        name='result'
    )
]
