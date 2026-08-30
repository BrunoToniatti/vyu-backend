from django.db import models
from main.models.base import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    class Meta:
        db_table = 'category'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class CategoryItem(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Categoria"
    )
    name = models.CharField(max_length=100, verbose_name="Nome do Item")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'category_item'
        verbose_name = 'Item de Categoria'
        verbose_name_plural = 'Itens de Categoria'
        ordering = ['category', 'name']
        unique_together = [('category', 'name')]

    def __str__(self):
        return f"{self.category.name} > {self.name}"
