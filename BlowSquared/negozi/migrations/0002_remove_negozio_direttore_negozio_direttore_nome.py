# Generated by Django 5.2.3 on 2025-07-12 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negozi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='negozio',
            name='direttore',
        ),
        migrations.AddField(
            model_name='negozio',
            name='direttore_nome',
            field=models.CharField(blank=True, help_text='Nome del direttore del punto vendita (legacy field)', max_length=100, null=True),
        ),
    ]
