from django.contrib import admin

from .models import Recipe, Tag, Ingredient

admin.site.register(Recipe)
# admin.site.register(ShoppingCart)
# admin.site.register(Favourite)
admin.site.register(Tag)
admin.site.register(Ingredient)
