# Generated by Django 5.2.3 on 2025-07-02 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utenti', '0002_profiloutente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profiloutente',
            name='latitudine',
        ),
        migrations.RemoveField(
            model_name='profiloutente',
            name='longitudine',
        ),
        migrations.AlterField(
            model_name='profiloutente',
            name='provincia',
            field=models.CharField(blank=True, help_text="Provincia dell'utente (sigla)", max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='profiloutente',
            name='raggio_ricerca_km',
            field=models.PositiveIntegerField(default=50, help_text='Raggio di ricerca in km per negozi vicini'),
        ),
    ]
