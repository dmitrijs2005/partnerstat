from django.contrib import admin

# Register your models here.

from .models import Viewing

class ViewingAdmin(admin.ModelAdmin):
    list_display = ('date', 'stream_type', 'threshold', 'user_qty','ips_qty',
                    'total_streams', 'avg_played_seconds', 'total_played_seconds', 'max_played_seconds')
    ordering = ['date', 'stream_type', 'threshold']

admin.site.register(Viewing, ViewingAdmin)