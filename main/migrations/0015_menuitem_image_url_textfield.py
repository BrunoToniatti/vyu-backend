from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_add_comanda_menu_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image_url',
            field=models.TextField(blank=True),
        ),
    ]
