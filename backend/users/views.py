from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import UserAvatarSerializer
from .models import Subscription

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from .serializers import UserWithRecipesSerializer
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Djoser-пользователи плюс экшены подписок."""

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
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
        self.pagination_class = LimitOffsetPagination
        queryset = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserWithRecipesSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserAvatarView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserAvatarSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.avatar = None
        instance.save(update_fields=['avatar'])


# class SubscribeView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request, pk):
#         author = get_object_or_404(User, pk=pk)
#         if request.user == author:
#             return Response({'detail': 'Нельзя подписаться на себя'},
#                             status=status.HTTP_400_BAD_REQUEST)
#         _, created = Subscription.objects.get_or_create(
#             user=request.user, author=author
#         )
#         if not created:
#             return Response({'detail': 'Вы уже подписаны'},
#                             status=status.HTTP_400_BAD_REQUEST)
#         serializer = UserWithRecipesSerializer(author, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def delete(self, request, pk):
#         author = get_object_or_404(User, pk=pk)
#         deleted, _ = Subscription.objects.filter(
#             user=request.user, author=author
#         ).delete()
#         if not deleted:
#             return Response(
#                 {'detail': 'Вы не подписаны на этого пользователя'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class SubscriptionsListView(ListAPIView):
#     serializer_class = UserWithRecipesSerializer
#     permission_classes = (IsAuthenticated,)
#     pagination_class = LimitOffsetPagination

#     def get_queryset(self):
#         return User.objects.filter(followers__user=self.request.user)
