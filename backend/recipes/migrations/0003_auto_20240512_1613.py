# Generated by Django 3.2.3 on 2024-05-12 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='recipe',
            new_name='recipe_url',
        ),
        migrations.AlterField(
            model_name='link',
            name='short_link',
            field=models.CharField(max_length=10, unique=True, verbose_name='Короткая ссылка на рецепт'),
        ),
    ]
