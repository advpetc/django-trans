from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import requests
from .models import TransSource, TransResult
import json
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages


def homepage(request):
    """
    Display the homepage
    """
    if request.method == 'POST':
        if TransSource.objects.filter(
                trans_source=request.POST['q'].strip(),
                trans_source_lang=request.POST['lang'],
                trans_source_type=request.POST['type']).exists():
            searched = 1
        else:
            searched = 0

        source = request.POST['q'].strip()

        if request.POST['lang'] == 'en' and request.POST['to'] == 'zh':
            engines = ['google', 'baidu', 'youdao', 'bing', 'atman']
        else:
            engines = ['google', 'baidu', 'youdao', 'bing']
        s = TransSource(trans_source=request.POST['q'],
                        trans_source_lang=request.POST['lang'],
                        trans_source_type=request.POST['type'], )
        s.save()
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

            if resp['errorCode'] == 0:
                s.transresult_set.create(
                    trans_output=resp['data'][0]['text'],
                    trans_time=str(timezone.now()),
                    trans_engine=engine,
                    trans_output_lang=request.POST['to'])
            else:
                messages.add_message(request, messages.ERROR, resp['errorMessage'] + " from " + engine)


        curr_trans_list = TransSource.objects.filter(
            trans_source=request.POST['q'],
            trans_source_lang=request.POST['lang'],
            trans_source_type=request.POST['type'])[0].transresult_set

        if curr_trans_list.count() != 0:
            not_empty = 1
        else:
            not_empty = 0
        context = {
            'source': source,
            'curr_trans_list': curr_trans_list.all,
            'not_empty': not_empty,
            'searched': searched,
        }
        return render(request, 'polls/homepage.html', context)
    else:
        latest_trans_list = TransResult.objects.order_by('trans_time')[:]
        context = {
            'latest_trans_list': latest_trans_list,
        }
        return render(request, 'polls/homepage.html', context)


def result(request, voteresult_id):
    """
    show result page
    """
    selected_trans = get_object_or_404(TransResult, pk=voteresult_id)
    selected_trans.vote_result += 1
    selected_trans.vote_time = timezone.now()
    selected_trans.save()
    source = selected_trans.trans_source
    all_trans_result = source.transresult_set.order_by('-vote_result')
    return render(request, 'polls/result.html', {'all_trans_result': all_trans_result,
                                                 'source': source.trans_source})


#
# def comment(request, id):
#     if request.method == 'POST':
#         selected_trans = get_object_or_404(TransResult, pk=id)
#         selected_trans.comment = request.POST['comment']
#         selected_trans.save()
#     return HttpResponseRedirect(reverse('polls/homepage', args=tra))

def search(request):
    """
    Go to search interface
    """
    if request.method == 'POST':
        # print(request.POST['start_time'])
        result_list = TransResult.objects.filter(
            trans_engine=request.POST['engine'],
            trans_time__range=[
                datetime.datetime.strptime(request.POST['start_time'], "%Y-%m-%d"),
                datetime.datetime.strptime(request.POST['end_time'], "%Y-%m-%d")
            ]
        )
        result_list.order_by('vote_result')
        jump_in = []
        for each_one in result_list:
            # print(each_one)
            source = each_one.trans_source
            all_trans_results = TransResult.objects.filter(trans_source=source)
            other_trans_results = all_trans_results.exclude(trans_engine=request.POST['engine'])

            snip_in = [each_one, other_trans_results]
            jump_in.append(snip_in)

        paginator = Paginator(jump_in, 25)  # Show 25 results per page

        page = request.GET.get('page')
        try:
            jump_in = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            jump_in = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            jump_in = paginator.page(paginator.num_pages)

        context = {
            'trans_results': jump_in,
            'start_time': request.POST['start_time'],
            'end_time': request.POST['end_time']
        }
        return render(request, 'polls/search.html', context)
    else:
        return render(request, 'polls/search.html')
