import json
from math import ceil

from django.db.models import Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect

from .models import Project, User, Result, Data, Source, TaskView

'''
Package only used for TransVote APP are shown below
'''

import queue
import os
import threading
import shlex
import requests
import datetime
import random
import subprocess
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from .models import TransSource, TransResult, TransHistory, TransUser


PROJECT_TYPE_ALL = 'ALL'
PROJECT_TYPE_DISTRIBUTE = "DISTRIBUTE"


def homepage(request):
    return render(request, 'homepage.html')


"""
Upon this point, all functions are used for Project APP
"""


def project_index(request):
    '''
    Index page.
    '''
    project_list_in = Project.objects.order_by('-create_time').all()
    paginator = Paginator(project_list_in, 10)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        project_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        project_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        project_list = paginator.page(paginator.num_pages)
    return render(request, 'project/project_list.html', {'project_list': project_list})


def project_summary(request, project_id):
    '''
    Summary page for a project.
    '''
    project = get_object_or_404(Project, pk=project_id)
    users_stat = []
    for user in project.users.all():
        users_stat.append({"name": user.name, "id": user.id, "finished": user.result_set.filter(project=project,
                                                                                                result__isnull=False).count()})
    return render(request, 'project/project_summary.html', {'project': project, "users_stat": users_stat})


def project_task(request, project_id, user_id):
    '''
    Task page for an user on a project.
    '''
    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(User, pk=user_id)
    print("user_id: %s, project_id: %s" % (user_id, project_id))
    data = None
    if project.project_type == PROJECT_TYPE_ALL:
        data_id_boundary = 0
        try:
            result = Result.objects.filter(user=user, project=project).order_by('-data')[0]
            data_id_boundary = result.data.id
        except IndexError:
            pass

        try:
            data = project.source.data_set.filter(id__gt = data_id_boundary)[0]
        except IndexError:
            return render(request, 'project/task_completion.html', {'project': project, 'user': user})
    elif project.project_type == PROJECT_TYPE_DISTRIBUTE:
        try:
            selected_choice = Result.objects.raw(
                " select * from project_result where project_id = %s and user_id = %s "
                " and result is null", [str(project_id), str(user_id)]
            )[0]
        except IndexError:
            return render(request, 'project/task_completion.html', {'project': project, 'user': user})
        data = selected_choice.data
    else:
        return HttpResponse('Unknow project type:' + project.project_type)

    finished=user.result_set.filter(project=project).count()
    return render(request,
        'project/task.html',
        {'project': project, 'task_view': project.task_view, 'user': user, 'data': data, 'finished': finished})


def project_result(request, project_id):
    '''
    Result page for a project. This page only displays a summary informaiton.
    '''
    project = get_object_or_404(Project, pk=project_id)
    project_result = Result.objects.filter(project=project)
    user_agg_result = project_result.values("result", "user__name").annotate(result_count=Count('result')).order_by("user__name")
    template_name = "default_result"
    if 'template_name' in request.GET and request.GET['template_name'] != "None":
        template_name = request.GET['template_name']
    return render(request,
        'project/result/%s.html' % template_name,
        {'user_agg_result': user_agg_result})


def project_result_details(request, project_id):
    '''
    Result details page for a project.
    '''

    template_name = "default_result_details"
    if 'template_name' in request.GET and request.GET['template_name'] != "None":
        template_name = request.GET['template_name']

    if template_name == "default_result_details":
        project = get_object_or_404(Project, pk=project_id)
        project_result = Result.objects.filter(project=project)

        return render(request,
            'project/result/%s.html' % template_name,
            {'project_result': project_result})

    elif template_name == "entity_result_details":
        project = get_object_or_404(Project, pk=project_id)
        project_result = Result.objects.filter(project=project)

        entity_result = []
        for item_result in project_result:
            username = item_result.user.name
            data_id = item_result.data.id
            result_json = json.loads(str(item_result.result))
            data_json = json.loads(str(item_result.data.json))["entities"]

            for i in range(len(result_json)):
                data_ith = data_json[i]
                entity_result.append(
                    {
                        "username": username,
                        "data_id": data_id,
                        "result": result_json[i],
                        "raw": data_ith["raw"],
                        "translation": data_ith["translation"]
                    })
        return render(request,
            'project/result/%s.html' % template_name,
            {'entity_result': entity_result})

    elif template_name == 'sentence_match_result_details':
        project = get_object_or_404(Project, pk=project_id)
        project_result = Result.objects.filter(project=project)

        sentences_result = []
        for item_result in project_result:
            username = item_result.user.name
            data_id = item_result.data.id
            result_json = json.loads(str(item_result.result))
            data_json = json.loads(str(item_result.data.json))["sentences"]

            for i in range(len(result_json)):
                data_ith = data_json[i]
                sentences_result.append(
                    {
                        "username": username,
                        "data_id": data_id,
                        "result": result_json[i],
                        "raw": data_ith["raw"],
                        "translation": data_ith["translation"]
                    })

        return render(request,
            'project/result/%s.html' % template_name,
            {'result': sentences_result})
    else:
        raise Http404("Unknow template for result_details page: %s" % template_name)


def project_answer(request, project_id, user_id, data_id):
    '''
    User's answer will be handled in this function.
    '''

    result_value = request.POST['result']
    comment = request.POST['comment']
    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(User, pk=user_id)
    data = get_object_or_404(Data, pk=data_id)
    result = Result.objects.raw(
        " select * from project_result where project_id = %s"
        " and user_id = %s and data_id = %s ", [str(project_id), str(user_id), str(data_id)]
    )[0]
    result.result = result_value
    result.comment = comment
    result.save()
    return redirect('project_task', project_id=project_id, user_id=user_id)


def project_new(request):
    '''
    To create a new project.
    '''
    if request.method == 'POST':
        name = request.POST['name']
        project_type = request.POST['project_type']
        result_details_view = request.POST['result_details_view']

        task_view_id = request.POST['task_view_id']
        task_view = None
        if not task_view_id:
            # TODO: add task view creation
            pass
        task_view = get_object_or_404(TaskView, pk=task_view_id)

        source_id = None
        source = None

        if "source_id" not in request.POST:
            source_name = request.POST['source_name']
            source = Source(name=source_name)
            source.save()
            data_file = request.FILES['file']
            for line in data_file:
                line = line.strip()
                if line:
                    data = Data(source=source, json=line)
                    data.save()
            source_id = source.id
        else:
            source_id = request.POST['source_id']
            source = get_object_or_404(Source, pk=source_id)

        users_id = request.POST.getlist('users')


        project = Project(
            name=name,
            project_type=project_type,
            task_view=task_view,
            result_details_view=result_details_view,
            source=source)
        project.save()

        for user_id in users_id:
            user = get_object_or_404(User, pk=user_id)
            project.users.add(user)

        if "source_id" not in request.POST and "dis_num" in request.POST:
            results_num_per_user = ceil(source.data_set.count() * int(request.POST["dis_num"]) / len(users_id))
            dis_num = int(request.POST["dis_num"])
            project.project_boundary = dis_num
            project.save()

            if dis_num >= len(users_id) and dis_num != 1:
                # TODO: add error page or pop up warning
                print('should not reach here')
                # return render_to_response('project_new', message="Invaild DISTRIBUTE number,"
                #                                                  " please be less than the number of users you choose")
            temp = {}
            for each_id in users_id:
                temp[each_id] = results_num_per_user

            for each_data in source.data_set.all():
                all_users = users_id[:]
                for _ in range(dis_num):
                    picked_user_id = random.choice(all_users)
                    if not all_users or temp[picked_user_id] == 0:
                        picked_user_id = random.choice(users_id)
                    else:
                        temp[picked_user_id] -= 1
                        all_users.remove(picked_user_id)
                    user = User.objects.get(pk=picked_user_id)

                    result = Result(project=project, data=each_data, user=user)
                    result.save()
        return redirect('project_index')
    else:
        return render(
            request,
            "project/project_new.html",
            {
                "task_views": TaskView.objects.all(),
                "sources": Source.objects.all(),
                "users": User.objects.all()
            })


def project_example(request, task_view_id):
    '''
    Example data for a task view.
    '''
    task_view = get_object_or_404(TaskView, pk=task_view_id)
    response = HttpResponse(task_view.data_example, content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename="data_example.json.txt"'

    return response


"""
Upon this point, all function below are exclusively used for TransVote App
"""


class Producer(threading.Thread):
    def __init__(self, command, engine_in, temp_source, engine, source_lang, source_to, source,
                 searched, user_trans, current_trans_list, request):
        threading.Thread.__init__(self)
        self.command = command
        self.engine_in = engine_in
        self.temp_source = temp_source
        self.engine = engine
        self.source_lang = source_lang
        self.source_to = source_to
        self.source = source
        # self.out_score = out_score
        self.searched = searched
        self.user_trans = user_trans
        self.current_trans_list = current_trans_list
        self.request = request
        self.setName(str(engine))

    def run(self):
        write_in = ""
        if len(self.engine) is 2:
            send = {
                'type': self.engine[0],
                'from': self.source_lang,
                'to': self.source_to,
                'q': [{'id': 1, 'text': self.source}],
                'extra': {
                    'domain': self.engine[1]
                }
            }
            write_in = self.engine[0] + " : " + self.engine[1]
        else:
            send = {
                "type": self.engine,
                "from": self.source_lang,
                "to": self.source_to,
                "q": [{"id": "1", "text": self.source}]
            }
            write_in = self.engine
        host = "http://translate.atman360.com/third_translate"
        headers = {
            'content-type': 'application/json;charset=utf-8',
            'accept': 'application/json'
        }
        r = requests.post(host, json=send, headers=headers)
        resp = json.loads(r.content.decode('utf-8'))
        # print(send)
        # print(resp)

        if resp['errorCode'] == 0:
            data = resp['data'][0]['text']
            engine_target = open(self.engine_in, 'w')
            if self.source_to == 'zh':
                engine_target.write(" ".join(data))
            else:
                engine_target.write(data)
            engine_target.close()
            if not self.user_trans == "":
                user = True
                with open(self.engine_in, 'r') as input_file:
                    score = subprocess.check_output(self.command, stdin=input_file)
                    # os.remove(self.engine_in)
            else:
                user = False
                score = None

            if self.searched:

                temp = TransResult.objects.filter(trans_source=self.temp_source,
                                                  trans_engine=write_in)
                if len(temp) == 1:
                    # print('reach1')
                    result_each = temp[0]
                    if not TransHistory.objects.filter(trans_result=result_each,
                                                       trans_content=data).exists():
                        # print('reach2')
                        his = TransHistory.objects.create(trans_result=result_each,
                                                          trans_content=data,
                                                          trans_time=str(timezone.now()))
                        self.current_trans_list.put(his)
                        if not user:
                            TransUser.objects.create(trans_his=his)
                        else:
                            TransUser.objects.create(trans_his=his,
                                                     score=score,
                                                     user_trans=self.user_trans)
                            his.bogus_score = score
                    else:
                        # print('reach3')
                        pre_his = TransHistory.objects.filter(trans_result=result_each,
                                                              trans_content=data)[0]
                        self.current_trans_list.put(pre_his)
                        if user:
                            TransUser.objects.create(trans_his=pre_his,
                                                     score=score,
                                                     user_trans=self.user_trans)
                            pre_his.bogus_score = score
                else:
                    # print('reach2')
                    new_result_temp = TransResult.objects.create(trans_source=self.temp_source,
                                                                 trans_engine=write_in)
                    new_his = TransHistory.objects.create(trans_result=new_result_temp,
                                                          trans_content=data,
                                                          trans_time=str(timezone.now()))
                    self.current_trans_list.put(new_his)
            else:
                new_result = TransResult.objects.create(trans_source=self.temp_source,
                                                        trans_engine=write_in)
                new_his = TransHistory.objects.create(trans_result=new_result,
                                                      trans_content=data,
                                                      trans_time=str(timezone.now()))

                self.current_trans_list.put(new_his)
                if user:
                    TransUser.objects.create(trans_his=new_his,
                                             score=score,
                                             user_trans=self.user_trans)
                    new_his.bogus_score = score

        else:
            messages.add_message(self.request, messages.ERROR, resp['errorMessage'] + " from " + write_in)


def transvote_translation(request, user_trans, source, source_lang, source_to):
    command = shlex.split('/usr/bin/perl multi-bleu.perl project/static/temp/reference')
    user_in = 'project/static/temp/reference'
    engine_in = 'project/static/temp/mt-output'

    user_target = open(user_in, 'w')
    if source_to == 'zh':
        user_target.write(" ".join(user_trans.strip()))
    else:
        user_target.write(user_trans.strip())
    user_target.close()

    if source_lang == 'en' and source_to == 'zh':
        engines = ['google', 'baidu', 'youdao', 'bing']
        if request.POST['medical'] == '1':
            engines.append(['atman', 'medical'])
        if request.POST['technology'] == '1':
            engines.append(['atman', 'technology'])
        if request.POST['political'] == '1':
            engines.append(['atman', 'political'])
    else:
        engines = ['google', 'baidu', 'youdao', 'bing']

    if TransSource.objects.filter(
            trans_source=source,
            trans_source_lang=source_lang,
            trans_output_lang=source_to
    ).exists():
        searched = True
    else:
        searched = False

    temp, created = TransSource.objects.get_or_create(trans_source=source,
                                                      trans_source_lang=source_lang,
                                                      trans_output_lang=source_to)
    current_trans_list = queue.Queue()
    # out_score = queue.Queue()
    random.shuffle(engines)
    threads = []
    for engine in engines:

        thread = Producer(command, engine_in, temp, engine, source_lang, source_to, source,
                          searched, user_trans, current_trans_list, request)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    os.remove(engine_in)
    os.remove(user_in)
    if not current_trans_list.empty():
        not_empty = 1
    else:
        not_empty = 0

    context = {
        'current_trans_list': list(current_trans_list.queue),
        'not_empty': not_empty,
        'searched': searched,
        # 'out_score': list(out_score.queue)
    }
    return context


def transvote_index(request):
    """
    Display the homepage
    """
    if request.method == 'POST':
        user_trans = request.POST['userTrans']
        source = request.POST['q'].strip()
        source_lang = request.POST['lang']
        source_to = request.POST['to']

        context = transvote_translation(request, user_trans, source, source_lang, source_to)

        return render(request, 'polls/trans_results.html', context)
    else:
        return render(request, 'polls/homepage.html')


def transvote_vote(request, voteresult_id):
    vote_item = get_object_or_404(TransHistory, pk=voteresult_id)
    vote_item.vote_result += 1
    vote_item.vote_time = timezone.now()
    vote_item.save()
    return render(request, 'polls/confirm.html', {'vote_item': vote_item})


def transvote_result(request, voteresult_id):
    """
    show result page
    """
    selected_trans = get_object_or_404(TransHistory, pk=voteresult_id)

    source = selected_trans.trans_result.trans_source
    all_trans_result = source.transresult_set
    try:
        comment = request.POST['comment']
    except KeyError:

        return render(request, 'polls/result.html', {'all_trans_result': all_trans_result,
                                                     'source': source.trans_source, 'id': voteresult_id,
                                                     'not_submitted': True})
    else:
        selected_trans.comment_set.create(
            comment=comment,
        )
        selected_trans.save()
        messages.add_message(request, messages.SUCCESS, "successfully saved your comment!")
        return render(request, 'polls/result.html', {'all_trans_result': all_trans_result,
                                                     'source': source.trans_source,
                                                     'id': voteresult_id,
                                                     'not_submitted': False})


def transvote_search(request):
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


def transvote_download(request):
    if request.method == 'POST':
        command = shlex.split('/usr/bin/perl multi-bleu.perl project/static/temp/user_file.txt')
        # file to be translated
        source_in_path = 'project/static/temp/source_file.txt'
        # user's translations
        user_in_path = 'project/static/temp/user_file.txt'

        source_file = request.FILES['source_file'].read()
        user_file = request.FILES['user_file'].read()

        # getting source file and write into file: source_file.txt
        source_target = open(source_in_path, 'wb')
        source_target.write(source_file.strip())
        source_target.close()
        with open(source_in_path) as f1:
            sources = f1.readlines()
            # source_target
        os.remove(source_in_path)
        sources = [x.strip() for x in sources]
        # print(sources)

        source_lang = request.POST['lang']
        source_to = request.POST['to']
        # getting user's translations and write into file: user_file.txt
        user_target = open(user_in_path, 'w')
        # print(type(user_file.strip()))
        # b' '.join(user_file)
        if source_to == 'zh':
            user_target.write(" ".join(user_file.decode('utf-8').strip()))
        else:
            user_target.write(user_file.decode('utf-8').strip())

        user_target.close()
        threads = []

        engine_path_header = "project/static/temp/"
        # translate by line
        holders = {}
        # results = queue.Queue()
        targets = {}
        if source_lang == 'en' and source_to == 'zh':
            engines = ['google', 'baidu', 'bing', 'youdao']
            if request.POST['med'] == '1':
                engines.append(['atman', 'medical'])
            if request.POST['tech'] == '1':
                engines.append(['atman', 'technology'])
            if request.POST['pol'] == '1':
                engines.append(['atman', 'political'])

        else:
            engines = ['google', 'baidu', 'bing', 'youdao']

        org = {}

        for engine in engines:
            data = queue.Queue()
            holders[str(engine)] = {'data': data}
            temp_engine = engine_path_header + str(engine) + ".txt"
            targets[str(engine)] = open(temp_engine, 'w')
            if source_to == 'zh':
                org_file_path = engine_path_header + str(engine) + '_download.txt'
                org[str(engine)] = open(org_file_path, 'w')
            # for source in sources:
            # print(engine)
            thread = Scorer(sources, engine, source_lang, source_to, data, request)
            thread.start()
            threads.append(thread)

        print(len(threads))
        for thread in threads:
            thread.join()
            # print(thread)
            while not holders[str(thread.getName())]['data'].empty():
                if source_to == 'zh':
                    targets[thread.getName()].write(" ".join(holders[str(thread.getName())]['data'].get() + '\n'))
                    # with open()
                    org[str(thread.getName())].write(holders[str(thread.getName())]['data'].get() + '\n')
                else:
                    targets[thread.getName()].write(holders[str(thread.getName())]['data'].get() + '\n')
        print('finish writing')

        download_links = {}
        for engine in engines:
            targets[str(engine)].close()
            each_engine = engine_path_header + str(engine) + '.txt'

            # print(result)
            download_links[str(engine)] = ['Not being scored for error(s)', '']

            with open(each_engine, 'r') as f:
                print('start scoring', engine)
                try:
                    score = subprocess.check_output(command, stdin=f)
                    download_links[str(engine)][0] = score
                except:
                    messages.add_message(request, messages.ERROR, 'Scoring error from ' + str(engine))
                    # return render(request, 'polls/download_list.html')
                    # raise Exception('Command exit with code 1')
                if source_to == 'zh':
                    download_links[str(engine)][1] = 'temp/' + str(engine) + '_download.txt'
                else:
                    download_links[str(engine)][1] = 'temp/' + str(engine) + '.txt'
                    #     result_target = open(result, 'wb')
                    #     result_target.write(score)
                    #     result_target.close()
            print(engine, ' that finished scoring\n')
            # os.remove(each_engine)

        os.remove(user_in_path)

        context = {'download_links': download_links}
        return render(request, 'polls/download_list.html', context)

    else:
        return render(request, 'polls/download.html')


class Scorer(threading.Thread):
    def __init__(self, sources, engine, source_lang, source_to, data, request):
        threading.Thread.__init__(self)
        self.sources = sources
        self.engine = engine
        self.source_lang = source_lang
        self.source_to = source_to
        self.data = data
        self.request = request
        self.setName(str(engine))

    def run(self):
        # for engine in self.engines:
        for source in self.sources:
            if not source.strip():
                continue
            write_in = ""
            if len(self.engine) is 2:
                send = {
                    "type": self.engine[0],
                    "from": self.source_lang,
                    "to": self.source_to,
                    "q": [{"id": "1", "text": source}],
                    "extra": {
                        "domain": self.engine[1]
                    }
                }
                # print(type(self.engine[1]))
                write_in = self.engine[0] + " : " + self.engine[1]
            else:
                send = {
                    "type": self.engine,
                    "from": self.source_lang,
                    "to": self.source_to,
                    "q": [{"id": "1", "text": source}]
                }
                write_in = self.engine
            host = "http://translate.atman360.com/third_translate"
            headers = {
                "content-type": "application/json;charset=utf-8",
                "accept": "application/json"
            }

            # print(send)
            try:
                r = requests.post(host, json=send, headers=headers)
            except:
                messages.add_message(self.request, messages.ERROR, 'Connection error')

            try:
                resp = json.loads(r.content.decode("utf-8"))
            except:
                messages.add_message(self.request, messages.ERROR, 'Parsing error')

            if resp["errorCode"] == 0:
                # if self.source_to == 'zh':
                #     self.data.put(" ".join(resp["data"][0]["text"].strip()))
                # else:
                self.data.put(resp["data"][0]["text"].strip())

            else:
                messages.add_message(self.request, messages.ERROR,
                                     str(resp["errorCode"]) + " : " + resp["errorMessage"] + " from " + str(send))
