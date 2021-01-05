from django.contrib import admin

from .models import Recipe, Tag

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)