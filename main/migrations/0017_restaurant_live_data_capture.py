from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_usermanager_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='live_data_capture',
            field=models.BooleanField(default=False, verbose_name='Captura de dados ao vivo (via Comandas)'),
        ),
    ]
