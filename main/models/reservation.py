from django.db import models
from main.models.base import TimeStampedModel


class Reservation(TimeStampedModel):
    STATUS_PENDING   = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pendente'),
        (STATUS_CONFIRMED, 'Confirmada'),
        (STATUS_CANCELLED, 'Cancelada'),
        (STATUS_COMPLETED, 'Concluída'),
    ]

    restaurant = models.ForeignKey(
        'main.Restaurant',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Restaurante',
    )
    user_app = models.ForeignKey(
        'main.UserApp',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservations',
        verbose_name='Usuário (se cadastrado)',
    )
    guest_name  = models.CharField(max_length=200, verbose_name='Nome do Cliente')
    guest_phone = models.CharField(max_length=30, verbose_name='Telefone do Cliente')
    guest_email = models.EmailField(max_length=255, blank=True, verbose_name='E-mail do Cliente')

    date       = models.DateField(verbose_name='Data da Reserva')
    time       = models.TimeField(verbose_name='Hora da Reserva')
    party_size = models.PositiveIntegerField(default=1, verbose_name='Número de Pessoas')
    notes      = models.TextField(blank=True, verbose_name='Observações')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Status',
    )

    class Meta:
        db_table = 'reservation'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['date', 'time']

    def __str__(self):
        return f"[{self.restaurant.name}] {self.guest_name} — {self.date} {self.time}"
