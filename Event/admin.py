from django.contrib import admin
from .models import Event
# Register your models here.

class AdminEvents(admin.ModelAdmin):
    list_display = ('eventname','lastDate')
    search_fields = ('eventname','lastDate')
    list_filter = ('eventname','lastDate')


admin.site.register(Event,AdminEvents)