# Generated by Django 5.2.3 on 2025-07-10 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negozi', '0001_initial'),
        ('prodotti', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prodotto',
            name='negozio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prodotti', to='negozi.negozio'),
        ),
    ]
