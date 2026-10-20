from django.contrib import admin

from .models import Recipes, Purchases, Favourites

admin.site.register(Recipes)
admin.site.register(Purchases)
admin.site.register(Favourites)
