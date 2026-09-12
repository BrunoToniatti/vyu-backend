from django.db import models
from main.models.base import TimeStampedModel


class ChatMessage(TimeStampedModel):
    SENDER_APP_USER = 'app_user'
    SENDER_RESTAURANT = 'restaurant'

    restaurant = models.ForeignKey(
        'main.Restaurant',
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Restaurante',
    )
    user_app = models.ForeignKey(
        'main.UserApp',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='chat_messages',
        verbose_name='Usuário',
    )
    sender_type = models.CharField(
        max_length=20,
        choices=[(SENDER_APP_USER, 'Usuário'), (SENDER_RESTAURANT, 'Restaurante')],
        default=SENDER_APP_USER,
    )
    text = models.TextField(max_length=1000, verbose_name='Mensagem')

    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
        verbose_name = 'Mensagem do Chat'
        verbose_name_plural = 'Mensagens do Chat'

    def __str__(self):
        sender = self.user_app.username if self.user_app else 'Restaurante'
        return f"[{self.restaurant.name}] {sender}: {self.text[:40]}"
