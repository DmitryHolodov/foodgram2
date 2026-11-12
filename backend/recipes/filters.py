import django_filters

from .models import Recipe, Tag, Ingredient


# class RecipeFilter(django_filters.FilterSet):
#     tags = django_filters.ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         to_field_name='slug',
#         queryset=Tag.objects.all(),
#     )
#     is_favorited = django_filters.BooleanFilter(
#         method='filter_is_favorited'
#     )
#     is_in_shopping_cart = django_filters.BooleanFilter(
#         method='filter_is_in_shopping_cart'
#     )

#     class Meta:
#         model = Recipe
#         fields = ('tags', 'author')

#     def filter_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if user.is_authenticated:
#             if value:
#                 return queryset.filter(in_favorites__user=user).distinct()
#             return queryset.exclude(in_favorites__user=user)
#         return queryset

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         user = self.request.user
#         if user.is_authenticated:
#             if value:
#                 return queryset.filter(in_carts__user=user).distinct()
#             return queryset.exclude(in_carts__user=user)
#         return queryset

class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def _filter_by_relation(self, queryset, related_name, value):
        if not value or not self.request.user.is_authenticated:
            return queryset
        is_true = str(value).lower() in ('1', 'true', 'yes')
        lookup = f'{related_name}__user'
        if is_true:
            return queryset.filter(**{lookup: self.request.user}).distinct()
        return queryset.exclude(**{lookup: self.request.user}).distinct()

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_by_relation(queryset, 'favorites', value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_by_relation(queryset, 'shopping_cart', value)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
