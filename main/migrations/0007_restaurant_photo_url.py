from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_add_review_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='photo_url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='URL da Foto (Cloudinary)'),
        ),
    ]
