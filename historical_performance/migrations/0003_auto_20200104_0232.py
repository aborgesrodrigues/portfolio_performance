# Generated by Django 3.0.2 on 2020-01-04 02:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('historical_performance', '0002_auto_20200103_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='performanceportfolio',
            name='portfolio',
        ),
        migrations.AddField(
            model_name='performanceportfolio',
            name='allocation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='performances', to='historical_performance.Allocation', verbose_name='Portfolio'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='allocation',
            name='percentage',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Real Percentage'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='allocations', to='historical_performance.Portfolio', verbose_name='Portfolio'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Quantity'),
        ),
    ]