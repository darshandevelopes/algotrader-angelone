# Generated by Django 5.0.7 on 2024-07-31 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_trade_exit_alter_trade_stop_loss'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='alerts_sent',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='trade',
            name='order_ids',
            field=models.JSONField(default=list),
        ),
    ]
