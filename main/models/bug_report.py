from django.db import models
from main.models.base import TimeStampedModel
from main.models.user_manager import UserManager


class BugReport(TimeStampedModel):
    """
    Bug report or support ticket opened by a Manager and handled by an Admin.
    """
    class Platform(models.TextChoices):
        WEB = 'WEB', 'Site Web'
        APP = 'APP', 'Aplicativo Mobile'
        BOTH = 'BOTH', 'Ambos'

    class Category(models.TextChoices):
        BUG = 'BUG', 'Bug'
        SUPPORT = 'SUPPORT', 'Suporte'
        IMPROVEMENT = 'IMPROVEMENT', 'Melhoria'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        IN_PROGRESS = 'IN_PROGRESS', 'Em Andamento'
        RESOLVED = 'RESOLVED', 'Resolvido'
        CLOSED = 'CLOSED', 'Fechado'

    opened_by = models.ForeignKey(
        UserManager,
        on_delete=models.CASCADE,
        related_name='bug_reports',
        db_column='opened_by_id',
        verbose_name="Aberto por"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    platform = models.CharField(
        max_length=10,
        choices=Platform.choices,
        verbose_name="Plataforma Afetada"
    )
    category = models.CharField(
        max_length=15,
        choices=Category.choices,
        default=Category.BUG,
        verbose_name="Categoria"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="Status"
    )
    admin_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Resposta do Admin"
    )
    resolved_by = models.ForeignKey(
        UserManager,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports',
        db_column='resolved_by_id',
        verbose_name="Resolvido por"
    )

    class Meta:
        db_table = 'bug_report'
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title} — {self.get_status_display()}"
