import base64

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from .utils import AddDeleteRelationMixin


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отдаёт список тегов без пагинации."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(AddDeleteRelationMixin, viewsets.ModelViewSet):
    """CRUD рецептов, избранное, корзина и выгрузка списка покупок."""

    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбирает сериализатор чтения или записи в зависимости от метода."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохраняет рецепт с текущим пользователем в качестве автора."""
        serializer.save(author=self.request.user)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт в base64-кодировке."""
        recipe = self.get_object()
        code = base64.b64encode(str(recipe.id).encode()).decode()
        short_link = request.build_absolute_uri(f'/s/{code}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное или удаляет из него."""
        return self.add_delete_relation(
            request, pk, Favorite,
            'Рецепт уже в избранном',
            'Рецепта нет в избранном'
        )

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Добавляет рецепт в корзину или удаляет из неё."""
        return self.add_delete_relation(
            request, pk, ShoppingCart,
            'Рецепт уже в списке покупок',
            'Рецепта нет в списке покупок'
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Отдаёт файл с суммой ингредиентов из корзины пользователя."""
        ingredients = (
            IngredientAmount.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = ['Список покупок:', '']
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            lines.append(f'{name} ({unit}) — {item["total"]}')

        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Отдаёт справочник ингредиентов с фильтром по началу названия."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class ShortLinkRedirectView(APIView):
    """Перенаправляет с короткой ссылки на страницу рецепта."""

    def get(self, request, code):
        recipe_id = int(base64.b64decode(code))
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return HttpResponseRedirect(
            reverse('recipes-detail', args=[recipe.id])
        )
