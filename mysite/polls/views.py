from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.urls import reverse
# from django.views import generic
from django.utils import timezone
import requests
from .models import TransSource, TransResult
import json
from django.template import loader


def homepage(request):
    '''
    Display the homepage
    '''
    if request.method == 'POST':
        # index(request)
        s = TransSource(trans_source=request.POST['q'],
                        trans_source_lang=request.POST['lang'],
                        trans_source_type=request.POST['type'])

        TransSource.objects.all().delete()
        engines = ['google', 'atman', 'baidu', 'youdao', 'bing']
        for engine in engines:
            send_API = {
                'type': engine,
                'from': s.trans_source_lang,
                'to': request.POST['to'],
                'q': [{'id': 1, 'text': s.trans_source}],
                'extra': {
                    'domain': s.trans_source_type,
                }
            }
            host = "http://translate.atman360.com/third_translate"
            headers = {
                'content-type': 'application/json;charset=utf-8',
                'accept': 'application/json'
            }
            r = requests.post(host, json=send_API, headers=headers)
            # print(str(r.content))
            resp = json.loads(r.content.decode('utf-8'))
            # print(resp)
            # print(resp["data"][0]["text"])
            s.save()
            # print(s.trans_source)
            # print(request.POST['to'])
            # print(type(request.POST['to']))
            # v = request.POST['to']
            # t = str(datetime.datetime.now())
            s.transresult_set.create(
                trans_output=resp["data"][0]["text"],
                trans_time=str(timezone.now()),
                trans_engine=engine,
                trans_output_lang=request.POST['to'])
            # s.save()
            # to_add.save()
            # s.save()
            # to_add.save()
            # print(to_add.trans_engine)
            # s.transresult_set.add(to_add)
            # s.save()

        curr_trans_list = s.transresult_set  # transResult obj s

        # print(curr_trans_list.count())
        if curr_trans_list.count() != 0:
            not_empty = 1
        else:
            not_empty = 0

        context = {
            'curr_trans_list': curr_trans_list,
            'trans_source': s,
            'not_empty': not_empty,
        }
        return render(request, 'polls/homepage.html', context)
    else:
        # if 'trans_item' in request.GET and request.GET['trans_item']:
        #     trans_item = request.GET['trans_item']
        #     trans_source = TransSource.objects.filter()
        latest_trans_list = TransResult.objects.order_by('trans_time')[:]
        context = {
            'latest_trans_list': latest_trans_list,
        }
        return render(request, 'polls/homepage.html', context)


# def index(request):
#     '''
#     Show the search result
#     '''
#     # print(request.POST)
#     # request.POST.json()
#     # request.POST[q]
#     s = TransSource(trans_source=request.POST['q'],
#                     trans_source_lang=request.POST['lang'],
#                     trans_source_type=request.POST['type'])
#
#     TransSource.objects.all().delete()
#     engines = ['google', 'atman', 'baidu', 'youdao', 'bing']
#     for engine in engines:
#         send_API = {
#             'type': engine,
#             'from': s.trans_source_lang,
#             'to': request.POST['to'],
#             'q': [{'id': 1, 'text': s.trans_source}],
#             'extra': {
#                 'domain': s.trans_source_type,
#             }
#         }
#         host = "http://translate.atman360.com/third_translate"
#         headers = {
#             'content-type': 'application/json;charset=utf-8',
#             'accept': 'application/json'
#         }
#         r = requests.post(host, json=send_API, headers=headers)
#         # print(str(r.content))
#         resp = json.loads(r.content.decode('utf-8'))
#         # print(resp)
#         # print(resp["data"][0]["text"])
#         s.save()
#         # print(s.trans_source)
#         # print(request.POST['to'])
#         # print(type(request.POST['to']))
#         # v = request.POST['to']
#         # t = str(datetime.datetime.now())
#         s.transresult_set.create(
#                 trans_output=resp["data"][0]["text"],
#                 trans_time=str(timezone.now()),
#                 trans_engine=engine,
#                 trans_output_lang=request.POST['to'])
#         # s.save()
#         # to_add.save()
#         # s.save()
#         # to_add.save()
#         # print(to_add.trans_engine)
#         # s.transresult_set.add(to_add)
#         # s.save()
#
#
#     curr_trans_list = s.transresult_set # transResult obj s
#
#     print(curr_trans_list.count())
#     if curr_trans_list.count() != 0:
#         not_empty = 1
#     else:
#         not_empty = 0
#
#     context = {
#         'curr_trans_list': curr_trans_list,
#         'trans_source': s,
#         'not_empty': not_empty,
#     }
#     return render(request, 'polls/homepage.html', context)

def result(request, voteresult_id):
    '''
    show result page
    '''
    selected_trans = get_object_or_404(TransResult, pk=voteresult_id)
    return render(request, 'polls/results.html', {'selected_trans': selected_trans})
