# Generated by Django 3.2.12 on 2022-04-13 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('talla', 'talla')], max_length=255),
        ),
    ]
