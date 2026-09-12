from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_userapp_photo_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sender_type', models.CharField(
                    choices=[('app_user', 'Usuário'), ('restaurant', 'Restaurante')],
                    default='app_user',
                    max_length=20,
                )),
                ('text', models.TextField(max_length=1000, verbose_name='Mensagem')),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chat_messages',
                    to='main.restaurant',
                    verbose_name='Restaurante',
                )),
                ('user_app', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='chat_messages',
                    to='main.userapp',
                    verbose_name='Usuário',
                )),
            ],
            options={
                'verbose_name': 'Mensagem do Chat',
                'verbose_name_plural': 'Mensagens do Chat',
                'db_table': 'chat_message',
                'ordering': ['created_at'],
            },
        ),
    ]
