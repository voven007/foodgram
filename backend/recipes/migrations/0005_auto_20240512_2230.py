# Generated by Django 3.2.3 on 2024-05-12 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_link_recipe_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='id',
        ),
        migrations.RemoveField(
            model_name='link',
            name='recipe_url',
        ),
        migrations.AddField(
            model_name='link',
            name='recipe',
            field=models.OneToOneField(default=123, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='recipes.recipe'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='link',
            name='short_link',
            field=models.CharField(max_length=20, unique=True, verbose_name='Короткая ссылка на рецепт'),
        ),
    ]