from django.contrib import admin

from .models import Recipe, Tag, Ingridient, RecipeIngridient


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


admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
