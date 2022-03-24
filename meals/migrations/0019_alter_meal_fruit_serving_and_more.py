# Generated by Django 4.0.3 on 2022-03-24 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0018_ingredient_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='fruit_serving',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='meal',
            name='vegetable_serving',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]