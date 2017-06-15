from django.contrib import admin

from .models import TransResult, TransSource, TransHistory, User, Comment
# Register your models here.
admin.site.register(TransSource)
admin.site.register(TransResult)
admin.site.register(TransHistory)
admin.site.register(User)
admin.site.register(Comment)