# Generated by Django 5.1.1 on 2024-10-10 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_app', '0004_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='numero_telephone',
            field=models.CharField(max_length=15),
        ),
    ]