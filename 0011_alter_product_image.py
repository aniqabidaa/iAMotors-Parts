# Generated by Django 5.0.4 on 2024-05-01 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_shipping_is_delivered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default='product-default.png', upload_to='products/'),
            preserve_default=False,
        ),
    ]