from django.urls import path, include
from users.views import UserAvatarView, UserViewSet
from recipes.views import TagViewSet, RecipeViewSet, IngredientViewSet
from rest_framework.routers import DefaultRouter

from recipes.views import ShortLinkRedirectView

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('users/me/avatar/', UserAvatarView.as_view(), name='user_avatar'),
    path('s/<str:code>/', ShortLinkRedirectView.as_view(), name='short-link'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
