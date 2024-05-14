from django.contrib import admin
from .models import (Ingredient,
                     Tag,
                     IngredientInRecipe,
                     Recipe,
                     Favorite,
                     ShoppingCart,
                     Link
                     )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',)
    list_editable = ()
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',)
    list_editable = ()
    search_fields = ('name',)
    list_filter = ()
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
        'number_to_favorites')
    list_editable = ()
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'

    @admin.display(description="Добавлено в избранное")
    def number_to_favorites(self, recipe):
        return recipe.recipe_favorite.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
        'favorite_date',)
    list_editable = ()
    search_fields = ('recipe',)
    list_filter = ()
    list_display_links = ('recipe',)
    empty_value_display = 'Не задано'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',)
    list_editable = ()
    search_fields = ('recipe',)
    list_filter = ()
    list_display_links = ('recipe',)
    empty_value_display = 'Не задано'


class LinkAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'base_link',
        'short_link',)
    list_editable = ()
    search_fields = ()
    list_filter = ()
    list_display_links = ()
    empty_value_display = 'Не задано'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Link, LinkAdmin)
