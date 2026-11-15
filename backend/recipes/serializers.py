from django.db import transaction
from rest_framework import serializers

from api.serializers import Base64ImageField
from users.serializers import UserSerializer

from .models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализует ингредиенты справочника."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Показывает ингредиент в рецепте с количеством."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True,
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализует теги: id, name, slug."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Читает рецепт с тегами, автором, ингредиентами и флагами."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source='ingredient_amounts', read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет, в избранном ли рецепт у текущего пользователя."""
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.favorites.filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, в корзине ли рецепт у текущего пользователя."""
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.shopping_cart.filter(user=user).exists())


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Создаёт и обновляет рецепт с ингредиентами и тегами."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        """Требует ингредиенты и теги при частичном обновлении."""
        if self.partial:
            for field_name in ('ingredients', 'tags'):
                if field_name not in attrs:
                    raise serializers.ValidationError(
                        {field_name: 'Обязательное поле.'}
                    )
        return super().validate(attrs)

    def validate_tags(self, value):
        """Проверяет непустоту и отсутствие дублей тегов."""
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return value

    def validate_ingredients(self, value):
        """Проверяет непустоту и отсутствие дублей ингредиентов."""
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def _save_m2m(self, recipe, tags, ingredients):
        """Связывает рецепт с тегами и ингредиентами через bulk_create."""
        recipe.tags.set(tags)
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создаёт рецепт и его связи в транзакции."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._save_m2m(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт и перезаписывает его связи."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredient_amounts.all().delete()
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                recipe=instance,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients
        )
        return instance
    # @transaction.atomic
    # def update(self, instance, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     instance = super().update(instance, validated_data)
    #     instance.tags.set(tags)
    #     instance.ingredient_amounts.all().delete()
    #     IngredientAmount.objects.bulk_create(
    #         IngredientAmount(
    #             recipe=instance,
    #             ingredient=item['id'],
    #             amount=item['amount'],
    #         )
    #         for item in ingredients
    #     )
    #     return instance

    def to_representation(self, instance):
        """Возвращает рецепт в формате RecipeReadSerializer."""
        return RecipeReadSerializer(instance, context=self.context).data
