# Generated by Django 4.2.7 on 2024-02-17 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_remove_pozycjazamowienia_autor_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pozycjazamowienia',
            name='ksiazka',
        ),
    ]
