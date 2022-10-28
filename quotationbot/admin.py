from django.contrib import admin
from .models import *
from django_object_actions import DjangoObjectActions
# Register your models here.

class QuotationAdmin(admin.ModelAdmin):
    fields = ('bucket_name', 'text', 'approved')
    list_display = ('id', 'bucket_name', 'text', 'approved')
    search_fields = ('bucket_name', 'text')
    
admin.site.register(Quotation, QuotationAdmin)


def set_channels_to_run(modeladmin, request, queryset):
    for channel in queryset:
        channel.mark_to_run()
set_channels_to_run.short_description = 'Mark selected to run now'

class ChannelAdmin(admin.ModelAdmin):

    fields = ('name', 'bots_enabled', 'bot_minimum_minutes', 'bot_maximum_minutes', 'enabled_buckets')
    list_display = ('id', 'name', 'bots_enabled')
    search_fields = ('name',)

    actions = [set_channels_to_run, ]

    
admin.site.register(Channel, ChannelAdmin)