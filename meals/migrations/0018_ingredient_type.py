# Generated by Django 4.0.3 on 2022-03-22 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0017_meal_fruit_meal_fruit_serving_meal_vegetable_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='type',
            field=models.CharField(default='standard', max_length=50),
        ),
    ]
