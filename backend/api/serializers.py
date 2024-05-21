from api.fields import Base64ImageField
from djoser.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Link,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription, User


class UserAvatarSerialiser(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингридиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для Избранного"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже добавлен!')]


class CustomUserSerializer(UserSerializer):
    """Сериализатор для Пользователя"""
    avatar = Base64ImageField(allow_null=True, required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Метод проверки подписки"""
        user = self.context.get('request').user
        if user.is_authenticated:
            if isinstance(obj, User):
                return Subscription.objects.filter(
                    author=obj, user=user).exists()
            return True
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Количества ингридиента в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        """Метод валидации количества"""

        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        """Метод валидации количества"""

        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        """Мета-параметры сериализатора"""

        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра Рецепта"""
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_list')
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        """Метод проверки на добавление в избранное."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки на присутствие в корзине."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и резактирования Рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0!')
        return value

    def validate(self, data):
        """Метод валидации ингредиентов"""
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть отмечено не меньше 1 тега')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными')

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients':
                'Должен быть хотя бы один ингредиент'})

        ingredient_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(pk=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Введен не существующий ингредиент')
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(item['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients':
                    ('Значение ингредиента должно быть больше 0')})
        data['ingredients'] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента"""

        for element in ingredients:
            id = element['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = element['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe,
                amount=amount
            )

    def create_tags(self, tags, recipe):
        """Метод добавления тега"""

        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели"""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""

        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод представления модели"""

        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data


class ShortLinkSerialiser(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""

    class Meta:
        model = Link
        fields = ('short_link',)

    def to_representation(self, instance):
        return {'short-link': instance.short_link}


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для Списка покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже добавлен!')]


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов короткий."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)


class ShowFollowSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """

    recipes = RecipesShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(default=True)

    class Meta:
        model = Subscription
        fields = ('id',
                  'user',
                  'author',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')
        read_only_fields = ('__all__',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author=obj.author)[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipesShortSerializer(
            queryset, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество подписок у пользователя."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Метод проверки подписки"""

        user = self.context.get('request').user
        if user.is_authenticated:
            if isinstance(obj, User):
                return Subscription.objects.filter(
                    author=obj, user=user).exists()
            return True
        return False


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = ('user',
                  'author',)

    def to_representation(self, instance):
        return ShowFollowSerializer(instance.author, context=self.context).data


class SubscriptionsSerializer(CustomUserSerializer):
    """[GET] Список авторов на которых подписан пользователь."""
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    avatar = serializers.ImageField(source='author.avatar')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'avatar',
                  'is_subscribed', 'recipes',
                  'recipes_count'
                  )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipe_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author=obj.author)[:recipe_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipesShortSerializer(
            queryset, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        """Метод проверки подписки"""
        request = self.context.get('request')
        return Subscription.objects.filter(
            author=obj.author, user=request.user).exists()


class SubscribedSerislizer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def to_representation(self, instanсe):
        request = self.context.get('request')
        context = {'request': request}
        serialiser = SubscriptionsSerializer(instanсe, context=context)
        return serialiser.data
