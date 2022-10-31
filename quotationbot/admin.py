from django.contrib import admin
from .models import *
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

    fields = ('name', 'bots_enabled', 'bot_minimum_minutes', 'bot_maximum_minutes', 'enabled_buckets',
        'is_needy_gf_channel', 'available_to_message_after')
    list_display = ('id', 'name', 'bots_enabled', 'is_needy_gf_channel', 'bot_minimum_minutes',
        'bot_maximum_minutes', 'available_to_message_after')
    search_fields = ('name',)
    readonly_fields = ["available_to_message_after"]

    actions = [set_channels_to_run, ]

admin.site.register(Channel, ChannelAdmin)

class ChatServerSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ["next_run_at"]


admin.site.register(ChatServerSettings, ChatServerSettingsAdmin)