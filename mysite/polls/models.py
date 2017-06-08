from django.db import models
import datetime


# Create your models here.
#
# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#     def __str__(self): # show the specific content instead of type
#         return self.question_text
#     def was_published_recently(self):
#         return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
#
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     def __str__(self):
#         return self.choice_text

# class Homepage(models.Model):
#     # search_id = models.CharField(max_length=200)
#     search_item = models.TextField()
#     search_lang = models.CharField(max_length=200)
#     trans_time = models.DateTimeField('time write in')
#     trans_engine = models.CharField(max_length=200)
#     trans_result = models.CharField(max_length=200)
#     trans_lang = models.CharField(max_length=200)

class TransSource(models.Model):
    trans_source = models.TextField(null=True)
    trans_source_lang = models.CharField(max_length=2, null=True)
    trans_source_type = models.CharField(max_length=2, null=True)
    def __str__(self):
        return self.trans_source


class TransResult(models.Model):
    # trans_source = models.TextField(null=True)
    trans_source = models.ForeignKey(TransSource, null=True, on_delete=models.CASCADE)
    trans_output = models.TextField(null=True)
    trans_time = models.DateTimeField(default=datetime.datetime.now)
    trans_engine = models.CharField(max_length=10, null=True)
    trans_output_lang = models.CharField(max_length=2, null=True)
    vote_result = models.IntegerField(default=0)
    vote_time = models.DateTimeField(default=datetime.datetime.now)
    def __str__(self):
        return self.trans_output


# class VoteResult(models.Model):
#     # vote_id = models.CharField(max_length=200)
#     # vote_result_id = models.CharField(max_length=200)
#     vote_result_id = models.ForeignKey(TransResult, null=True)  # Each vote result can map to a transResult
#     vote_result = models.IntegerField(default=0)
#     vote_time = models.DateTimeField(default=datetime.datetime.now)
#     def __str__(self):
#         return self.vote_result