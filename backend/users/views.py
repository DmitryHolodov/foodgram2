from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import default_token_generator
from rest_framework import permissions, status, viewsets
# from rest_framework.response import Response
from rest_framework.views import APIView


User = get_user_model()


class SignUpView(APIView):
    """Эндпоинт регистрации."""

    pass
    # permission_classes = (permissions.AllowAny,)

    # def post(self, request):
    #     serializer = SignUpSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()

    #     code = default_token_generator.make_token(user)
    #     send_confirmation_email(user.email, code)

    #     return Response(
    #         {'email': user.email, 'username': user.username},
    #         status=status.HTTP_200_OK,
    #     )


class TokenView(APIView):
    """Эндпоинт получения токена."""
    pass
    # permission_classes = (permissions.AllowAny,)

    # def post(self, request):
    #     serializer = TokenSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     return Response({'token': serializer.validated_data['token']})


class UserViewSet(viewsets.ModelViewSet):
    """API для управления пользователями (только админ)."""
    pass
    # queryset = User.objects.all().order_by('username')
    # serializer_class = UserSerializer
    # permission_classes = (IsAdmin,)
    # search_fields = ('username',)
    # lookup_field = 'username'
    # http_method_names = ['get', 'post', 'patch', 'delete']
