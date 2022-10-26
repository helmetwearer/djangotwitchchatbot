from django.contrib import admin
from .models import *
# Register your models here.

class QuotationAdmin(admin.ModelAdmin):
    fields = ('bucket_name', 'text', 'approved')
    list_display = ('id', 'bucket_name', 'text', 'approved')
    search_fields = ('bucket_name', 'text')
    
admin.site.register(Quotation, QuotationAdmin)


class ChannelAdmin(admin.ModelAdmin):
    fields = ('name', 'bots_enabled', 'bot_minimum_minutes', 'bot_maximum_minutes', 'enabled_buckets')
    list_display = ('id', 'name', 'bots_enabled')
    search_fields = ('name',)
    
admin.site.register(Channel, ChannelAdmin)