from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_restaurant_photo_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapp',
            name='photo_url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='URL da Foto (Cloudinary)'),
        ),
    ]
