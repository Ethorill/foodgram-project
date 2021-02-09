from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.translation import gettext_lazy as _

from .models import (Recipe,
                     Tag,
                     Ingridient,
                     RecipeIngridient,
                     FavoriteRecipe,
                     FollowUser,
                     ShopingList)


class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class FollowUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('title', 'measurement_unit',)
    list_filter = ('title',)


class RecipeIngridientInline(admin.StackedInline):
    model = RecipeIngridient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'count_fav',)
    list_filter = ('author', 'title', 'tag',)
    inlines = (RecipeIngridientInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)


admin.site.register(ShopingList, ShopListAdmin)
admin.site.register(FollowUser, FollowUserAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
