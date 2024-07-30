# Generated by Django 5.0.7 on 2024-07-30 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_trade_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='exit',
            field=models.DecimalField(decimal_places=2, default=-1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='trade',
            name='stop_loss',
            field=models.DecimalField(decimal_places=2, default=-1, max_digits=10),
        ),
    ]