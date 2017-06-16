from django.db import models


# Create your models here.
#
class TransSource(models.Model):
    trans_source = models.TextField(null=True)
    trans_source_lang = models.CharField(max_length=2, null=True)
    trans_source_type = models.CharField(max_length=2, null=True)
    trans_output_lang = models.CharField(max_length=2, null=True)

    def __str__(self):
        return self.trans_source


class TransResult(models.Model):
    trans_source = models.ForeignKey(TransSource, null=True, on_delete=models.CASCADE)
    trans_engine = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.trans_engine


class TransHistory(models.Model):
    trans_result = models.ForeignKey(TransResult, null=True, on_delete=models.CASCADE)
    trans_content = models.TextField(null=True)
    trans_time = models.DateTimeField(null=True, blank=True)
    vote_result = models.IntegerField(default=0)
    vote_time = models.DateTimeField(null=True, blank=True)
    bogus_score = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.trans_content


class User(models.Model):
    trans_his = models.ForeignKey(TransHistory, null=True, on_delete=models.CASCADE)
    score = models.CharField(max_length=100, null=True)
    user_trans = models.TextField(null=True)

    def __str__(self):
        return self.user_trans


class Comment(models.Model):
    trans_his = models.ForeignKey(TransHistory, null=True, on_delete=models.CASCADE)
    comment = models.TextField(null=True)

    def __str__(self):
        return self.comment
