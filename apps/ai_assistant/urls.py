"""
==========================================================================
 AI ASSISTANT URLS - Routing untuk Chat API & Halaman Pengaturan
==========================================================================
 /ai/             → Halaman utama AI Assistant (pengaturan)
 /ai/chat/        → POST API chat AI (AJAX)
 /ai/insight/     → GET Auto insight harian
 /ai/feedback/    → POST Feedback 👍/👎
 /ai/history/     → GET Riwayat chat
 /ai/clear/       → POST Hapus riwayat chat
==========================================================================
"""
from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.AIAssistantSettingsView.as_view(), name='index'),
    path('dashboard/', views.AIDashboardView.as_view(), name='dashboard'),
    path('chat/', views.ai_chat_api, name='chat'),
    path('insight/', views.auto_insight, name='insight'),
    path('feedback/', views.chat_feedback, name='feedback'),
    path('history/', views.chat_history_api, name='history'),
    path('clear/', views.clear_history, name='clear'),
]
