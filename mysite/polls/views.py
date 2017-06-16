from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import requests
from .models import TransSource, TransResult, TransHistory, User
import json
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import subprocess
from subprocess import PIPE
import shlex


def homepage(request):
    """
    Display the homepage
    """
    if request.method == 'POST':
        user_trans = request.POST['userTrans']
        command = shlex.split('/usr/bin/perl multi-bleu.perl reference')
        user_in = 'reference'
        engine_in = 'mt-output'

        source = request.POST['q'].strip()
        source_lang = request.POST['lang']
        source_type = request.POST['type']

        source_to = request.POST['to']

        user_target = open(user_in, 'w')
        if source_to == 'zh':
            user_target.write(" ".join(user_trans))
        else:
            user_target.write(user_trans)
        user_target.close()

        if source_lang == 'en' and source_to == 'zh':
            engines = ['google', 'baidu', 'youdao', 'bing', 'atman']
        else:
            engines = ['google', 'baidu', 'youdao', 'bing']

        if TransSource.objects.filter(
                trans_source=source,
                trans_source_lang=source_lang,
                trans_source_type=source_type,
                trans_output_lang=source_to
        ).exists():
            searched = True
        else:
            searched = False

        temp, created = TransSource.objects.get_or_create(trans_source=source,
                                                          trans_source_lang=source_lang,
                                                          trans_source_type=source_type,
                                                          trans_output_lang=source_to)
        current_trans_list = []
        out_score = []
        for engine in engines:
            send = {
                'type': engine,
                'from': source_lang,
                'to': source_to,
                'q': [{'id': 1, 'text': source}],
                'extra': {
                    'domain': source_type,
                }
            }
            host = "http://translate.atman360.com/third_translate"
            headers = {
                'content-type': 'application/json;charset=utf-8',
                'accept': 'application/json'
            }
            r = requests.post(host, json=send, headers=headers)
            resp = json.loads(r.content.decode('utf-8'))

            if resp['errorCode'] == 0:
                data = resp['data'][0]['text']
                engine_target = open(engine_in, 'w')
                if source_to == 'zh':
                    engine_target.write(" ".join(data))
                else:
                    engine_target.write(data)
                engine_target.close()
                if not user_trans == "":
                    user = True
                    with open(engine_in, 'r') as input_file:

                        score = subprocess.check_output(command, stdin=input_file)
                        out_score.append(score)
                else:
                    user = False

                if searched:
                    result_each = TransResult.objects.filter(trans_source=temp,
                                                             trans_engine=engine)[0]
                    if not TransHistory.objects.filter(trans_result=result_each,
                                                       trans_content=data).exists():

                        his = TransHistory.objects.create(trans_result=result_each,
                                                          trans_content=data,
                                                          trans_time=str(timezone.now()))
                        current_trans_list.append(his)
                        if not user:
                            User.objects.create(trans_his=his)
                        else:
                            User.objects.create(trans_his=his,
                                                score=score,
                                                user_trans=user_trans)
                    else:
                        pre_his = TransHistory.objects.filter(trans_result=result_each,
                                                              trans_content=data)[0]
                        current_trans_list.append(pre_his)
                        if user:
                            User.objects.create(trans_his=pre_his,
                                                score=score,
                                                user_trans=user_trans)
                else:
                    new_result = TransResult.objects.create(trans_source=temp,
                                                            trans_engine=engine)
                    new_his = TransHistory.objects.create(trans_result=new_result,
                                                          trans_content=data,
                                                          trans_time=str(timezone.now()))

                    current_trans_list.append(new_his)
                    if user:
                        User.objects.create(trans_his=new_his,
                                            score=score,
                                            user_trans=user_trans)

            else:
                messages.add_message(request, messages.ERROR, resp['errorMessage'] + " from " + engine)

        if current_trans_list.count != 0:
            not_empty = 1
        else:
            not_empty = 0
        context = {
            'current_trans_list': current_trans_list,
            'not_empty': not_empty,
            'searched': searched,
            'source_type': source_type,
            'out_score': out_score
        }
        return render(request, 'polls/trans_results.html', context)
    else:
        return render(request, 'polls/homepage.html')


def result(request, voteresult_id):
    """
    show result page
    """
    selected_trans = get_object_or_404(TransHistory, pk=voteresult_id)
    try:
        comment = request.POST['comment']
    except KeyError:
        selected_trans.vote_result += 1
        selected_trans.vote_time = timezone.now()
        selected_trans.save()
        source = selected_trans.trans_result.trans_source
        all_trans_result = source.transresult_set
        return render(request, 'polls/result.html', {'all_trans_result': all_trans_result, 'id': voteresult_id,
                                                     'source': source.trans_source})
    else:
        selected_trans.comment_set.create(
            comment=comment,
        )
        selected_trans.save()
        messages.add_message(request, messages.SUCCESS, "successfully saved your comment!")
        return render(request, 'polls/result.html')
        # return HttpResponseRedirect(reverse('polls:result', args=(voteresult_id,)))


def search(request):
    """
    Go to search interface
    """
    if request.method == 'POST':
        results = TransResult.objects.filter(trans_engine=request.POST['engine'])
        all_his = []
        jump_in = []
        for each_result in results:
            all_his_from = TransHistory.objects.filter(trans_result=each_result,
                                                       trans_time__range=[datetime.datetime.strptime(
                                                           request.POST['start_time'], "%Y-%m-%d"),
                                                           datetime.datetime.strptime(
                                                               request.POST['end_time'], "%Y-%m-%d")])

            for each_his in all_his_from:
                all_other_result = TransResult.objects.filter(trans_source=each_result.trans_source
                                                              ).exclude(trans_engine=request.POST['engine'])
                tie_with = []
                tie_with.append(each_his)
                for each_other_result in all_other_result:
                    all_other_his = TransHistory.objects.filter(trans_result=each_other_result)
                    tie_with += all_other_his
                    # all_other_result = TransResult.objects.filter(trans_source=each_result.trans_source
                    #                                               ).exclude(trans_engine=request.POST['engine'])
                    # for each_other_result in all_other_result:
                    #     all_his += TransHistory.objects.filter(trans_result=each_other_result)
                all_his.append(tie_with)
                jump_in += tie_with

        paginator = Paginator(all_his, 5)  # Show 25 results per page

        page = request.POST['page']
        try:
            his = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            his = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            his = paginator.page(paginator.num_pages)

        context = {
            'search_engine': request.POST['engine'],
            'all_results': jump_in,
            'trans_results': his}
        return render(request, 'polls/search_results.html', context)
    else:
        return render(request, 'polls/search.html')
