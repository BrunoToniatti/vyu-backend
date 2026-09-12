from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_increase_lat_lng_precision'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado Em')),
                ('stars', models.PositiveSmallIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(5),
                    ],
                    verbose_name='Estrelas'
                )),
                ('comment', models.TextField(blank=True, default='', verbose_name='Comentário')),
                ('manager_response', models.TextField(blank=True, null=True, verbose_name='Resposta do Gerente')),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to='main.restaurant',
                    verbose_name='Restaurante'
                )),
                ('user_app', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to='main.userapp',
                    verbose_name='Usuário'
                )),
            ],
            options={
                'verbose_name': 'Avaliação',
                'verbose_name_plural': 'Avaliações',
                'db_table': 'review',
                'ordering': ['-created_at'],
                'unique_together': {('user_app', 'restaurant')},
            },
        ),
    ]
