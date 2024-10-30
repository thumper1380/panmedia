from .models import Log
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html



class LogAdmin(admin.ModelAdmin):
    # filter
    list_display = ('id', 'get_level_display', 'message', 'get_model_name', 'created_at')
    list_filter = ('level', 'created_at',)


    def get_model_name(self, obj):
        obj: Log
        return obj.model_name

    def get_level_display(self, obj):
        obj: Log
        color = obj.color
        return format_html(f'<span style="color: {color}">{obj.level_name}</span>')


    get_model_name.short_description = 'Model'
    get_level_display.short_description = 'Level'

    # custom filter
    # def get_queryset(self, request):
    #     qs = super(LogAdmin, self).get_queryset(request)
    #     return qs.filter(content_type=ContentType.objects.get_for_model(MyCustomModel))


admin.site.register(Log, LogAdmin)
