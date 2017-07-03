from django.contrib import admin

# Register your models here.
from .models import Data, User, TaskView, Project, Source, Result

admin.site.register(Data)
admin.site.register(User)
admin.site.register(TaskView)
admin.site.register(Project)
admin.site.register(Source)
admin.site.register(Result)