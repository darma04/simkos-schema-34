from django.contrib import admin
from .models import AIAssistantConfig, ChatHistory, ChatFeedback


@admin.register(AIAssistantConfig)
class AIAssistantConfigAdmin(admin.ModelAdmin):
    list_display = ('provider', 'model_name', 'aktif', 'diupdate_pada')


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'short_message', 'intent', 'source', 'created_at')
    list_filter = ('role', 'intent', 'user', 'created_at')
    search_fields = ('message', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Pesan'


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback', 'short_text', 'created_at')
    list_filter = ('feedback', 'user', 'created_at')
    ordering = ('-created_at',)

    def short_text(self, obj):
        return obj.message_text[:80] + '...' if len(obj.message_text) > 80 else obj.message_text
    short_text.short_description = 'Teks AI'
