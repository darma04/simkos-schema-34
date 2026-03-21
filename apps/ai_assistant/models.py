"""
==========================================================================
 AI ASSISTANT MODELS - Konfigurasi, Riwayat Chat & Feedback
==========================================================================
 Model:
 1. AIAssistantConfig — Singleton konfigurasi provider/API key
 2. ChatHistory — Riwayat percakapan per user (context memory)
 3. ChatFeedback — Feedback 👍/👎 dari user untuk setiap respons AI
==========================================================================
"""
from django.db import models
from django.conf import settings


class AIAssistantConfig(models.Model):
    """Model singleton untuk konfigurasi AI Chat Assistant."""

    PROVIDER_CHOICES = (
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI ChatGPT'),
        ('groq', 'Groq (Gratis)'),
    )

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='groq',
        verbose_name="Provider AI"
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="API Key",
        help_text="API Key dari Google AI Studio, OpenAI Platform, atau Groq Console"
    )
    model_name = models.CharField(
        max_length=100,
        default='llama-3.3-70b-versatile',
        verbose_name="Model AI",
        help_text="Contoh: gemini-2.0-flash, gpt-4o-mini, llama-3.3-70b-versatile"
    )
    aktif = models.BooleanField(
        default=True,
        verbose_name="Status Aktif",
        help_text="Aktifkan/nonaktifkan fitur AI Chat"
    )
    ai_name = models.CharField(
        max_length=100,
        default='AI Assistant',
        verbose_name="Nama AI",
        help_text="Nama yang ditampilkan di header chat AI"
    )
    max_tokens = models.IntegerField(
        default=1024,
        verbose_name="Max Tokens",
        help_text="Batas maksimal token respons AI"
    )
    temperature = models.FloatField(
        default=0.7,
        verbose_name="Temperature",
        help_text="Kreativitas AI (0.0 = fokus, 1.0 = kreatif)"
    )
    system_prompt = models.TextField(
        blank=True,
        default='',
        verbose_name="System Prompt Tambahan",
        help_text="Instruksi tambahan untuk AI (opsional)"
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pengaturan AI Assistant"
        verbose_name_plural = "Pengaturan AI Assistant"

    def __str__(self):
        return f"AI Assistant ({self.get_provider_display()})"

    def save(self, *args, **kwargs):
        """Singleton pattern — paksa pk=1."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Memuat konfigurasi AI (buat default jika belum ada)."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ChatHistory(models.Model):
    """Riwayat chat per user — mendukung context memory & multi-user."""

    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chat_history',
        verbose_name="User"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name="Role"
    )
    message = models.TextField(
        verbose_name="Pesan"
    )
    intent = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Intent Terdeteksi"
    )
    source = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Sumber AI"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu"
    )

    class Meta:
        verbose_name = "Riwayat Chat"
        verbose_name_plural = "Riwayat Chat"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        preview = self.message[:50] + '...' if len(self.message) > 50 else self.message
        return f"[{self.role}] {preview}"


class ChatFeedback(models.Model):
    """Feedback 👍/👎 dari user untuk respons AI."""

    FEEDBACK_CHOICES = (
        ('up', '👍 Bagus'),
        ('down', '👎 Kurang'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chat_feedback',
        verbose_name="User"
    )
    chat = models.ForeignKey(
        ChatHistory,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name="Chat",
        null=True,
        blank=True,
    )
    feedback = models.CharField(
        max_length=4,
        choices=FEEDBACK_CHOICES,
        verbose_name="Feedback"
    )
    message_text = models.TextField(
        blank=True,
        default='',
        verbose_name="Teks Pesan AI"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu"
    )

    class Meta:
        verbose_name = "Feedback Chat"
        verbose_name_plural = "Feedback Chat"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_display()} oleh {self.user}"
