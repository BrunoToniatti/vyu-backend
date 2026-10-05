from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_menuitem_image_url_textfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermanager',
            name='plan',
            field=models.CharField(
                choices=[('BASIC', 'Basic'), ('PRO', 'Pro')],
                default='BASIC',
                max_length=10,
                verbose_name='Plano',
            ),
        ),
    ]
