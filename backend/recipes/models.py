from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram_backend.constants import (
    MAX_SLUG_LENGTH,
    MAX_RECIPE_NAME_LENGTH,
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    """Метка рецепта с уникальным slug"""
    name = models.CharField(
        'Название',
        max_length=MAX_SLUG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_SLUG_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Справочник ингредиентов: название и единица измерения."""
    name = models.CharField(
        'Ингредиент',
        max_length=MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_unit',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт с автором, текстом, картинкой и временем приготовления."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_RECIPE_NAME_LENGTH
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/'
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Промежуточная модель «рецепт — ингредиент» с количеством."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.ingredient}: {self.amount}'


class Favorite(models.Model):
    """Отметка «в избранном»: пара пользователь — рецепт, без дублей."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favourite',
            )
        ]


class ShoppingCart(models.Model):
    """Корзина покупок: пара пользователь — рецепт для выгрузки списка."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            )
        ]
