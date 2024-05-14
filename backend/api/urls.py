from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    GetShortLink,
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    UserViewSet,
    SubscriptionViewSet
)

app_name = 'api'
router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('recipes/<int:recipe_id>/get-link/', GetShortLink.as_view()),
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
