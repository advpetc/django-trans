from django.db import models
import datetime


# Create your models here.
#
class TransSource(models.Model):
    trans_source = models.TextField(null=True)
    trans_source_lang = models.CharField(max_length=2, null=True)
    trans_source_type = models.CharField(max_length=2, null=True)

    def __str__(self):
        return self.trans_source


class TransResult(models.Model):
    trans_source = models.ForeignKey(TransSource, null=True, on_delete=models.CASCADE)
    trans_output = models.TextField(null=True)
    trans_time = models.DateTimeField(default=datetime.datetime.now)
    trans_engine = models.CharField(max_length=10, null=True)
    trans_output_lang = models.CharField(max_length=2, null=True)
    vote_result = models.IntegerField(default=0)
    vote_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.trans_output
