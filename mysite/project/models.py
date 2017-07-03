from django.db import models

"""
Upon this point, all models are used for Project APP
"""


class Source(models.Model):
    name = models.CharField(max_length=256)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Data(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    json = models.TextField()

    def __str__(self):
        return "%r, %r" % (self.source, self.json)


class TaskView(models.Model):
    name = models.CharField(max_length=256)
    javascript = models.TextField()
    html = models.TextField()
    data_example = models.TextField(null=True, blank=True, default=None)
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField()

    # user_boundary = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=256)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    task_view = models.ForeignKey(TaskView, on_delete=models.CASCADE)
    project_type = models.CharField(max_length=64)
    users = models.ManyToManyField(User)
    create_time = models.DateTimeField(auto_now=True)
    result_details_view = models.CharField(max_length=256, null=True, blank=True, default=None)
    project_boundary = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Result(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    result = models.CharField(max_length=4096, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'data', 'project')

    def __str__(self):
        return "%r, %r, %r, %r" % (self.project, self.user, self.data, self.result)


"""
Upon this point, all models are used for Project APP
"""


class TransSource(models.Model):
    trans_source = models.TextField(null=True)
    trans_source_lang = models.CharField(max_length=2, null=True)
    # trans_source_type = models.CharField(max_length=2, null=True)
    trans_output_lang = models.CharField(max_length=2, null=True)

    def __str__(self):
        return self.trans_source


class TransResult(models.Model):
    trans_source = models.ForeignKey(TransSource, null=True, on_delete=models.CASCADE)
    trans_engine = models.CharField(max_length=30, null=True)

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


class TransUser(models.Model):
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
