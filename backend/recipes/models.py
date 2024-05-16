from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from rest_framework.reverse import reverse

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=128
    )
    measurement_unit = models.CharField(
        verbose_name='Единица изменения',
        max_length=64,
        db_index=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        verbose_name='Название тега',
        db_index=True,
        unique=True,
        max_length=32
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=32,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Недопустимый символ в Слаге Тега'
        )]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_recipe',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        db_index=True,
        max_length=256
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipes/images'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient_recipe',
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tag_recipe',
        verbose_name='Теги'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    direct_link = models.URLField(
        verbose_name='Прямая ссылка на рецепт',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('api:recipes-detail', kwargs={'pk': self.pk})


class Link(models.Model):
    """Модель короткой ссылки"""
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        primary_key=True
    )
    base_link = models.URLField(
        verbose_name='Прямая ссылка на рецепт',
        blank=True
    )
    short_link = models.CharField(
        max_length=20,
        verbose_name='Короткая ссылка на рецепт',
        unique=False
    )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return self.short_link

    # def save(self, *args, **kwargs):
    #     if not self.short_link:
    #         self.short_link = str(uuid.uuid4())[:6]
    #     super().save(*args, **kwargs)


class IngredientInRecipe(models.Model):
    """Модель количества ингредиента в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_list',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(
                1, message='Минимальное значение 1')]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='уникальное значение')]

    def __str__(self):
        return f'{self.ingredient} – {self.amount}'


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorite',
        verbose_name='Рецепт'
    )
    favorite_date = models.DateTimeField(
        verbose_name='Дата добавления в избранное',
        auto_now_add=True
    )

    class Meta:
        ordering = ('favorite_date',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart')]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в свою корзину'
