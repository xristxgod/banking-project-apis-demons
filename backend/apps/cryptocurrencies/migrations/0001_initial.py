# Generated by Django 4.2.2 on 2023-06-20 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('chain_id', models.IntegerField(blank=True, null=True, verbose_name='Chain id')),
                ('url', models.URLField(blank=True, null=True, verbose_name='Node url')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Network',
                'verbose_name_plural': 'Networks',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('symbol', models.CharField(max_length=255, verbose_name='Symbol')),
                ('decimal_place', models.IntegerField(default=6, verbose_name='Decimal place')),
                ('address', models.CharField(blank=True, max_length=50, null=True, verbose_name='Contract address')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='currencies', to='cryptocurrencies.network', verbose_name='Network')),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
        ),
    ]
