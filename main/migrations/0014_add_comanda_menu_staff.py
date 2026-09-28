import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_add_checkin_to_reservation'),
    ]

    operations = [
        # ── MenuItem ──────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_url', models.URLField(blank=True, max_length=500)),
                ('category', models.CharField(
                    choices=[('FOOD', 'Comida'), ('DRINK', 'Bebida'), ('DESSERT', 'Sobremesa'), ('OTHER', 'Outro')],
                    default='FOOD', max_length=20,
                )),
                ('subcategory', models.CharField(blank=True, max_length=100)),
                ('available', models.BooleanField(default=True)),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='menu_items',
                    to='main.restaurant',
                )),
            ],
            options={'db_table': 'menu_item', 'ordering': ['category', 'name']},
        ),

        # ── RestaurantTable ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='RestaurantTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('identifier', models.CharField(max_length=50)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True)),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tables',
                    to='main.restaurant',
                )),
            ],
            options={'db_table': 'restaurant_table', 'ordering': ['identifier']},
        ),
        migrations.AddConstraint(
            model_name='restauranttable',
            constraint=models.UniqueConstraint(fields=['restaurant', 'identifier'], name='unique_restaurant_table'),
        ),

        # ── Comanda ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Comanda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('table_label', models.CharField(blank=True, max_length=50)),
                ('opened_by', models.CharField(max_length=150)),
                ('status', models.CharField(
                    choices=[('OPEN', 'Aberta'), ('CLOSED', 'Fechada')],
                    default='OPEN', max_length=10,
                )),
                ('notes', models.TextField(blank=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comandas',
                    to='main.restaurant',
                )),
                ('table', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='comandas',
                    to='main.restauranttable',
                )),
            ],
            options={'db_table': 'comanda', 'ordering': ['-created_at']},
        ),

        # ── ComandaItem ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ComandaItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200)),
                ('item_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('notes', models.CharField(blank=True, max_length=300)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('comanda', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='main.comanda',
                )),
                ('menu_item', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='main.menuitem',
                )),
            ],
            options={'db_table': 'comanda_item', 'ordering': ['added_at']},
        ),

        # ── StaffToken ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='StaffToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('staff_name', models.CharField(max_length=150)),
                ('token', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='staff_tokens',
                    to='main.restaurant',
                )),
            ],
            options={'db_table': 'staff_token', 'ordering': ['-created_at']},
        ),
    ]
