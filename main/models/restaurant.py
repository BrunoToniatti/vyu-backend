from django.db import models
from main.models.base import TimeStampedModel
from main.models.user_manager import UserManager


class Restaurant(TimeStampedModel):
    """
    Restaurant entity created and administered by a UserManager.
    """
    cnpj = models.CharField(max_length=20, db_index=True, verbose_name="CNPJ")
    manager = models.ForeignKey(
        UserManager,
        on_delete=models.CASCADE,
        related_name='restaurants',
        db_column='manager_id',
        verbose_name="Gerente Responsável"
    )
    contact_phone = models.CharField(max_length=20, verbose_name="Telefone de Contato")
    name = models.CharField(max_length=200, db_index=True, verbose_name="Nome do Restaurante")
    address = models.TextField(verbose_name="Endereço Completo")
    site = models.URLField(max_length=255, null=True, blank=True, verbose_name="Site Oficial")
    instagram = models.CharField(max_length=100, null=True, blank=True, verbose_name="Perfil do Instagram")
    path_logo = models.CharField(max_length=255, null=True, blank=True, verbose_name="Caminho do Logo")

    class Meta:
        db_table = 'restaurant'
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (CNPJ: {self.cnpj})"
