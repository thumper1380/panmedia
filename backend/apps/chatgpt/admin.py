from django.contrib import admin
from .models import Message, Conversation, ConversationSummary
from django.utils.safestring import mark_safe


class ConversationSummaryInline(admin.TabularInline):
    model = ConversationSummary
    extra = 0
    readonly_fields = ['content', 'created_at']
    exclude = ['updated_at']

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['get_message', 'is_summarized']
    
    # exclude fields
    exclude = ['content', 'created_at' ,'name', 'role', 'summarized_at']


    def is_summarized(self, obj):
        return obj.summarized_at != None
    
    is_summarized.boolean = True
    is_summarized.short_description = 'Summarized'

    def get_created_at(self, obj):
        # return  in "2 min ago" format
        return obj.created_at.strftime("%b %d, %Y, %H:%M:%S")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_message(self, obj):
        # return message bubble like whatsapp messagenger
        time = obj.created_at.strftime("%b %d, %Y, %H:%M:%S")
        if obj.role == 'user':  # use width fit-conten, also add time to message bubble like whatsapp, in gray color
            return mark_safe(f'<div style="background-color: #DCF8C6; padding: 10px; border-radius: 10px; width: fit-content; float: left;">{obj.content}<br><small style="color: gray;">{time}</small></div>')
        elif obj.role == 'assistant':
            # align right
            return mark_safe(f'<div style="background-color: #e1f3ff; padding: 10px; border-radius: 10px; width: fit-content; float: right;">{obj.content}<br><small style="color: gray;">{time}</small></div>')
        elif obj.role == 'function':
            return mark_safe(f'<div style="background-color: #FFF9C4; padding: 10px; border-radius: 10px; width: fit-content; float: right;">{obj.content}<br><small style="color: gray;">{time}</small></div>')
        elif obj.role == 'system':
            return mark_safe(f'<div style="background-color: #f7d4e0; padding: 10px; border-radius: 10px; width: fit-content; float: right;">{obj.content}<br><small style="color: gray;">{time}</small></div>')

class ConversationAdmin(admin.ModelAdmin):
    inlines = [ConversationSummaryInline, MessageInline]
    list_display = ['user', 'created_at']
    search_fields = ['user__email']


    class Meta:
        model = Conversation

    def clear_conversation(self, request, queryset):
        for conv in queryset:
            conv.clear()

    clear_conversation.short_description = "Clear Conversation"

    actions = [clear_conversation]


admin.site.register(Conversation, ConversationAdmin)
