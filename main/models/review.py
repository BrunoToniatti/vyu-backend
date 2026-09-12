from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from main.models.base import TimeStampedModel


class Review(TimeStampedModel):
    user_app = models.ForeignKey(
        'main.UserApp',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Usuário'
    )
    restaurant = models.ForeignKey(
        'main.Restaurant',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Restaurante'
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Estrelas'
    )
    comment = models.TextField(blank=True, default='', verbose_name='Comentário')
    manager_response = models.TextField(blank=True, null=True, verbose_name='Resposta do Gerente')

    class Meta:
        db_table = 'review'
        unique_together = ('user_app', 'restaurant')
        ordering = ['-created_at']
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'

    def __str__(self):
        return f"{self.user_app} → {self.restaurant} ({self.stars}★)"
