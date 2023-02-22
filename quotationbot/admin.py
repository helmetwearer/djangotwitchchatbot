from django.contrib import admin
from .models import *
# Register your models here.

class QuotationAdmin(admin.ModelAdmin):
    fields = ('bucket_name', 'text', 'approved')
    list_display = ('id', 'bucket_name', 'text', 'approved')
    search_fields = ('bucket_name', 'text')
    list_filter = ('bucket_name', 'approved')
    
admin.site.register(Quotation, QuotationAdmin)

def set_channels_to_run(modeladmin, request, queryset):
    for channel in queryset:
        channel.mark_to_run()
set_channels_to_run.short_description = 'Mark selected to run now'

# is there a way to use kwargs to make this one function?
def disable_selected_channels(modeladmin, request, queryset):
    for channel in queryset:
        channel.bots_enabled = False
        channel.save()
disable_selected_channels.short_description = 'Disable selected channels'

def enable_selected_channels(modeladmin, request, queryset):
    for channel in queryset:
        channel.bots_enabled = True
        channel.save()
enable_selected_channels.short_description = 'Enable selected channels'

class ChannelAdmin(admin.ModelAdmin):

    fields = ('name', 'bots_enabled', 'bot_minimum_minutes', 'bot_maximum_minutes', 'enabled_buckets',
        'is_imessage_server', 'available_to_message_after')
    list_display = ('id', 'name', 'bots_enabled', 'is_imessage_server', 'bot_minimum_minutes',
        'bot_maximum_minutes', 'available_to_message_after')
    search_fields = ('name',)
    readonly_fields = ["available_to_message_after"]
    list_filter = ('bots_enabled', 'is_imessage_server')

    actions = [set_channels_to_run, disable_selected_channels, enable_selected_channels]

admin.site.register(Channel, ChannelAdmin)

class ChatServerSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ["next_run_at"]


admin.site.register(ChatServerSettings, ChatServerSettingsAdmin)