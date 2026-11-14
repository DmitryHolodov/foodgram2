from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.serializers import Base64ImageField
from recipes.models import Recipe
User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Обновляет аватар текущего пользователя."""
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализует пользователя с вычисляемым полем is_subscribed."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.subscriptions.filter(author=obj).exists()


class SignUpSerializer(serializers.ModelSerializer):
    """Регистрирует пользователя с хешированием пароля."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        """Создаёт пользователя через create_user с хешированным паролем."""
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сокращённый рецепт для вложенных списков."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(UserSerializer):
    """Список пользователя-автора с его рецептами и их числом."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Отдаёт рецепты автора с учётом параметра recipes_limit."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        queryset = obj.recipes.all()
        if limit and limit.isdigit() and int(limit) > 0:
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Возвращает число рецептов автора."""
        return obj.recipes.count()
