from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
# from django.views import generic
import datetime
from .models import TransSource, TransResult, VoteResult
from django.template import loader


#
# def check(request, trans_id):

# def current_datatime(request):
#     now = datetime.datetime.now()

def index(request):
    '''
    Display the homepage
    '''
    # if request.method == 'POST':


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
    return render(request, 'polls/results.html', {'selected_trans': selected_trans})

# def vote(request, source_id):
#     source = get_object_or_404(TransSource, pk=source_id)
#     try:
#         selected_result = source.transresult_set.get(pk=request.POST['transresult'])
#     except(KeyError, TransResult.DoesNotExist):
#         return render(request, 'polls/results.html',{
#             'transsource': source,
#             'error_msg': "You didn't select a choice.",
#         })
#     else:
#         selected_result.vote_result += 1
#         selected_result.save()
#         return HttpResponseRedirect(reverse('polls:results', args=(source.id,)))


# class IndexView(generic.ListView):
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'
#
#     def get_queryset(self):
#         """Return the last five published questions."""
#         return Question.objects.order_by('-pub_date')[:5]
#
#
# class DetailView(generic.DetailView):
#     model = Question
#     template_name = 'polls/detail.html'
#
#
# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'
#
#
# def vote(request, question_id):
#     # same as above, no changes needed.
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

# def search(request):
#     if request.method == 'POST':
#         homepage = get_object_or_404(Homepage)
#         try:
#             input_item = homepage.search_item
