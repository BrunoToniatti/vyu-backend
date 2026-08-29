from django.db import models
from main.models.base import TimeStampedModel
from main.models.restaurant import Restaurant


class Queue(TimeStampedModel):
    """
    Queue entity tracking the current waiting line for a restaurant.
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Aberta'
        CLOSED = 'CLOSED', 'Fechada'
        PAUSED = 'PAUSED', 'Pausada'

    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='queue',
        db_column='restaurant_id',
        verbose_name="Restaurante"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CLOSED,
        verbose_name="Status da Fila"
    )
    current_size = models.PositiveIntegerField(default=0, verbose_name="Tamanho Atual da Fila")
    estimated_wait_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Tempo de Espera Estimado (minutos)"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        db_table = 'queue'
        verbose_name = 'Fila'
        verbose_name_plural = 'Filas'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Fila de {self.restaurant.name} — {self.get_status_display()} ({self.current_size} pessoas)"
