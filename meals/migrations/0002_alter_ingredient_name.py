# Generated by Django 4.0.1 on 2022-02-11 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
