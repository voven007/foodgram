from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (GetShortLink, IngredientViewSet, RecipeViewSet,
                    SubscriptionViewSet, TagViewSet, UserViewSet)

app_name = 'api'
router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('recipes/<int:recipe_id>/get-link/', GetShortLink.as_view()),
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
