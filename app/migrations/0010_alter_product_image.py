# Generated by Django 5.1.7 on 2025-04-13 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_product_digital'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='default.png', null=True, upload_to=''),
        ),
    ]
