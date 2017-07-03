from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^project/$', views.project_index, name='project_index'),
    url(r'^project/new/$', views.project_new, name='project_new'),
    url(r'^project/task_view/example/(?P<task_view_id>[0-9]+)/', views.project_example, name='project_example'),
    url(r'^project/(?P<project_id>[0-9]+)/$', views.project_summary, name='project_summary'),
    url(r'^project/(?P<project_id>[0-9]+)/(?P<user_id>[0-9]+)/task/$', views.project_task, name='project_task'),
    url(r'^project/(?P<project_id>[0-9]+)/result/$', views.project_result, name='project_result'),
    url(r'^project/(?P<project_id>[0-9]+)/result_details/$', views.project_result_details, name='project_result_details'),
    url(r'^project/(?P<project_id>[0-9]+)/(?P<user_id>[0-9]+)/(?P<data_id>[0-9]+)/answer/$', views.project_answer, name='project_answer'),

    # urls below are for transvote

    url(r'^polls/$', views.transvote_index, name='transvote_index'),
    url(r'^polls/search/$', views.transvote_search, name='transvote_search'),
    url(r'^polls/(?P<voteresult_id>[0-9]+)/$', views.transvote_vote, name='transvote_vote'),
    url(r'^polls/result/(?P<voteresult_id>[0-9]+)/$', views.transvote_result, name='transvote_result'),
    url(r'^polls/download/$', views.transvote_download, name='transvote_download'),
]
