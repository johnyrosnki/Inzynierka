# Generated by Django 4.2.7 on 2024-02-17 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_remove_pozycjazamowienia_ksiazka_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pozycjazamowienia',
            name='autor',
        ),
        migrations.RemoveField(
            model_name='pozycjazamowienia',
            name='tytul',
        ),
        migrations.AddField(
            model_name='pozycjazamowienia',
            name='ksiazka',
            field=models.ForeignKey(default=16, on_delete=django.db.models.deletion.CASCADE, to='mainapp.ksiazka', verbose_name='Książka'),
        ),
    ]
