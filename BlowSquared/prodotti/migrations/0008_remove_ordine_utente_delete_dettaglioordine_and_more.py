# Generated by Django 5.2.3 on 2025-07-15 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prodotti', '0007_alter_prodotto_sconto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordine',
            name='utente',
        ),
        migrations.DeleteModel(
            name='DettaglioOrdine',
        ),
        migrations.DeleteModel(
            name='Ordine',
        ),
    ]
