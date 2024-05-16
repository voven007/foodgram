import random
import string

from api.serializers import (CustomUserSerializer, IngredientSerializer,
                             RecipeSerializer, RecipesShortSerializer,
                             RecipeWriteSerializer, ShortLinkSerialiser,
                             SubscribedSerislizer, SubscriptionsSerializer,
                             TagSerializer, UserAvatarSerialiser)
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Link,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPagination
from .permissions import IsOwnerAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class UserViewSet(UserViewSet):
    """ViewSet для оработки Пользователей"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_permissions(self):
        """
        Переопределяем get_permissions для доступа только авторизованным
        пользователям к эндпоинту users/me/.
        """
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    """
    Доработать после решения всех проблем.
    @action(detail=False,
            permission_classes=[IsAuthenticated, ],
            serializer_class=SubscriptionsSerializer,
            url_path='subscriptions', url_name='subscriptions'
            )
    def subscriptions(self, request):
        Метод для отображения списка подписок пользователя.
        Реализация эндпоинта users/subscriptions/

        user = self.request.user
        return user.subscriber.all()
    """

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,),
            url_path='subscribe', url_name='subscribe'
            )
    def subscribe(self, request, id):
        """Метод для управления подписками """
        user = request.user
        author = get_object_or_404(User, id=id)
        change_subscription_status = Subscription.objects.filter(
            user=user.id, author=author.id)
        serializer = SubscribedSerislizer(
            data={'user': user.id, 'author': author.id},
            context={'request': request})

        if request.method == 'POST':
            if user == author:
                return Response('Вы пытаетесь подписаться на себя!!',
                                status=status.HTTP_400_BAD_REQUEST)
            if change_subscription_status.exists():
                return Response(f'Вы уже подписаны на {author}',
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if change_subscription_status.exists():
            change_subscription_status.delete()
            return Response(f'Вы отписались от {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET', 'PUT'],
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar', url_name='avatar'
            )
    def apply_avatar(self, request):
        """Метод для работы с аватаром"""
        serializer = UserAvatarSerialiser(
            self.request.user, data=request.data)
        if request.method == 'PUT' or 'GET':
            if (serializer.is_valid() and 'avatar' in request.data):
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @apply_avatar.mapping.delete
    def delete_avatar(self, request):
        """Метод для удаления аватара"""
        serializer = UserAvatarSerialiser(
            self.request.user, data=request.data)
        if (serializer.is_valid()):
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet Для модели рецептов"""
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerAdminOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора по методу запроса"""
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='favorite', url_name='favorite',)
    def favorite(self, request, pk):
        """Метод для управления избранными подписками """
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_400_BAD_REQUEST)

            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                               f'он уже есть в избранном у пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipesShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_404_NOT_FOUND)
            obj = Favorite.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'В избранном нет рецепта \"{recipe.name}\"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart',
            )
    def shopping_cart(self, request, pk):
        """Метод для управления списком покупок"""
        user = request.user
        if request.method == 'POST':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_400_BAD_REQUEST)
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                               f'он уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipesShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                recipe = get_object_or_404(Recipe, id=pk)
            except Http404:
                return Response('Рецепт не найден',
                                status=status.HTTP_404_NOT_FOUND)
            obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Нельзя удалить рецепт - \"{recipe.name}\", '
                           f'которого нет в списке покупок '},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Метод для объединения ингредиентов в список для загрузки"""

        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return shopping_list

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated, ],
            url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            )
    def download_shopping_cart(self, request):
        """Метод для загрузки ингредиентов и их количества
         для выбранных рецептов"""

        ingredients = IngredientInRecipe.objects.filter(
            recipe__recipe_shopping__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')


class SubscriptionViewSet(ListAPIView):
    """ViewSet для отображения страницы подписок пользователя"""
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user = self.request.user
        return user.subscriber.all()


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choices(characters, k=4))
    return "http:/localhost/s/" + short_url


class GetShortLink(APIView):
    repmission_classes = (AllowAny,)

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        short_url = generate_short_url()
        link_obj, _ = Link.objects.get_or_create(
            recipe=recipe,
            defaults={'base_link': recipe.get_absolute_url(),
                      'short_link': short_url}
        )
        serializer = ShortLinkSerialiser(link_obj)
        return Response(serializer.data)


def redirect_to_full_link(request, short_link):
    try:
        link_obj = Link.objects.get(
            short_link="http:/localhost/s/" + short_link
        )
        full_link = link_obj.base_link.replace('/api', '', 1)
        return redirect(full_link)
    except Link.DoesNotExist:
        return HttpResponse(
            'Ссылка не найдена', status=status.HTTP_404_NOT_FOUND)
