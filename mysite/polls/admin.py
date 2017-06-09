from django.contrib import admin

from .models import TransResult, TransSource
# Register your models here.
admin.site.register(TransSource)
admin.site.register(TransResult)
