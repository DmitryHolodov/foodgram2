from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from .models import Recipe
from users.serializers import RecipeShortSerializer


class AddDeleteRelationMixin:
    """POST добавляет связь с рецептом, DELETE — убирает."""

    def add_delete_relation(self, request, pk, model, exists_msg, missing_msg):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if model.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {'detail': exists_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'detail': missing_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
