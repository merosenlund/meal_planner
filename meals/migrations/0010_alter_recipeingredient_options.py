# Generated by Django 4.0.3 on 2022-03-16 02:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0009_remove_ingredient_recipes_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ['id']},
        ),
    ]
