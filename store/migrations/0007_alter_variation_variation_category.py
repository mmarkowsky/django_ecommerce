# Generated by Django 3.2.12 on 2022-04-27 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_variation_variation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('talla', 'talla'), ('color', 'color')], max_length=255),
        ),
    ]