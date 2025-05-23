# Generated by Django 4.2.20 on 2025-05-14 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_orders', '0003_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('shipped', 'Shipped'), ('ready_for_pickup', 'Ready for pickup'), ('delivered', 'Delivered'), ('returned', 'Returned'), ('unclaimed', 'Unclaimed')], db_index=True, default='shipped', max_length=20),
        ),
    ]
