# Generated by Django 5.0.7 on 2024-07-22 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_trade_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='status',
            field=models.CharField(default='Pending', max_length=10),
        ),
    ]