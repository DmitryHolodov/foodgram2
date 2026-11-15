from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import UserAvatarSerializer, UserWithRecipesSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Пользователи Djoser плюс подписки и смена аватара."""

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Подписывает на автора или отписывает с проверкой повторов и себя."""
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                    user=request.user, author=author).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=request.user, author=author)
            serializer = UserWithRecipesSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=request.user, author_id=id
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Отдаёт список авторов, на которых подписан пользователь."""
        self.pagination_class = LimitOffsetPagination
        queryset = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserAvatarView(RetrieveUpdateDestroyAPIView):
    """Показывает, обновляет и удаляет аватар текущего пользователя."""

    serializer_class = UserAvatarSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Возвращает текущего пользователя вместо объекта из URL."""
        return self.request.user

    def perform_destroy(self, instance):
        """Обнуляет аватар, не удаляя самого пользователя."""
        instance.avatar = None
        instance.save(update_fields=['avatar'])
