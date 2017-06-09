from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import requests
from .models import TransSource, TransResult
import json


def homepage(request):
    '''
    Display the homepage
    '''
    if request.method == 'POST':
        if TransSource.objects.filter(trans_source=request.POST['q'],
                                      trans_source_lang=request.POST['lang'],
                                      trans_source_type=request.POST['type']).exists():
            pass
        else:
            engines = ['google', 'atman', 'baidu', 'youdao', 'bing']
            s = TransSource(trans_source=request.POST['q'],
                            trans_source_lang=request.POST['lang'],
                            trans_source_type=request.POST['type'])
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
                resp = json.loads(r.content.decode('utf-8'))
                s.save()
                s.transresult_set.create(
                    trans_output=resp["data"][0]["text"],
                    trans_time=str(timezone.now()),
                    trans_engine=engine,
                    trans_output_lang=request.POST['to'])

        curr_trans_list = TransSource.objects.filter(
            trans_source=request.POST['q'],
            trans_source_lang=request.POST['lang'],
            trans_source_type=request.POST['type'])[0].transresult_set

        if curr_trans_list.count() != 0:
            not_empty = 1
        else:
            not_empty = 0

        context = {
            'curr_trans_list': curr_trans_list,
            'not_empty': not_empty,
        }
        return render(request, 'polls/homepage.html', context)
    else:
        latest_trans_list = TransResult.objects.order_by('trans_time')[:]
        context = {
            'latest_trans_list': latest_trans_list,
        }
        return render(request, 'polls/homepage.html', context)


def result(request, voteresult_id):
    '''
    show result page
    '''
    selected_trans = get_object_or_404(TransResult, pk=voteresult_id)
    selected_trans.vote_result += 1
    selected_trans.vote_time = timezone.now()
    selected_trans.save()
    return render(request, 'polls/results.html', {'selected_trans': selected_trans})
