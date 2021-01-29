from django.contrib import admin

from .models import Recipe, Tag, Ingridient, RecipeIngridient, FavoriteRecipe, FollowUser

class FollowUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

class IngridientAdmin(admin.ModelAdmin):
    list_display = ('title', 'measurement_unit', )

class RecipeIngridientInline(admin.StackedInline):
    model = RecipeIngridient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', )
    list_filter = ('author', 'title', 'tag', )
    inlines = (RecipeIngridientInline,)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', )


admin.site.register(FollowUser, FollowUserAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
