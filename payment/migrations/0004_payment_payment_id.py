# Generated by Django 5.1.6 on 2025-06-06 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
