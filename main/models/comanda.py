import uuid
from django.db import models
from main.models.base import TimeStampedModel
from main.models.restaurant import Restaurant


class MenuItem(TimeStampedModel):
    CATEGORY_FOOD    = 'FOOD'
    CATEGORY_DRINK   = 'DRINK'
    CATEGORY_DESSERT = 'DESSERT'
    CATEGORY_OTHER   = 'OTHER'
    CATEGORY_CHOICES = [
        (CATEGORY_FOOD,    'Comida'),
        (CATEGORY_DRINK,   'Bebida'),
        (CATEGORY_DESSERT, 'Sobremesa'),
        (CATEGORY_OTHER,   'Outro'),
    ]

    restaurant  = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image_url   = models.URLField(max_length=500, blank=True)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_FOOD)
    subcategory = models.CharField(max_length=100, blank=True)
    available   = models.BooleanField(default=True)

    class Meta:
        db_table = 'menu_item'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class RestaurantTable(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    identifier = models.CharField(max_length=50)  # e.g. "1", "VIP", "Terraço A"
    capacity   = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'restaurant_table'
        unique_together = [('restaurant', 'identifier')]
        ordering = ['identifier']

    def __str__(self):
        return f"Mesa {self.identifier} — {self.restaurant.name}"


class Comanda(TimeStampedModel):
    STATUS_OPEN   = 'OPEN'
    STATUS_CLOSED = 'CLOSED'
    STATUS_CHOICES = [
        (STATUS_OPEN,   'Aberta'),
        (STATUS_CLOSED, 'Fechada'),
    ]

    restaurant  = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='comandas')
    table       = models.ForeignKey(RestaurantTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='comandas')
    table_label = models.CharField(max_length=50, blank=True)  # snapshot
    opened_by   = models.CharField(max_length=150)             # staff name or "Manager"
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    notes       = models.TextField(blank=True)
    closed_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'comanda'
        ordering = ['-created_at']

    @property
    def total(self):
        return sum(i.subtotal for i in self.items.all())

    def __str__(self):
        label = self.table_label or f"Comanda #{self.pk}"
        return f"{label} — {self.get_status_display()}"


class ComandaItem(models.Model):
    comanda    = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='items')
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name  = models.CharField(max_length=200)           # snapshot
    item_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    quantity   = models.PositiveIntegerField(default=1)
    notes      = models.CharField(max_length=300, blank=True)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comanda_item'
        ordering = ['added_at']

    @property
    def subtotal(self):
        return self.item_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.item_name}"


class StaffToken(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff_tokens')
    staff_name = models.CharField(max_length=150)
    token      = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    active     = models.BooleanField(default=True)

    class Meta:
        db_table = 'staff_token'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.staff_name} — {self.restaurant.name}"
