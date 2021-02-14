from django import forms
from django.shortcuts import get_object_or_404

from .models import Recipe, Tag, RecipeIngridient, Ingridient


class RecipeForm(forms.ModelForm):

    def check_tags(self, tags):
        if tags:
            return True
        else:
            return False

    def check_ingr(self, ingr):
        if ingr:
            return True
        else:
            return False

    def add_ingr(self, request_ingr, recipe, delete_recipe: bool,):
        for i in request_ingr:
            try:
                RecipeIngridient.objects.create(
                    ingridient=get_object_or_404(Ingridient, title=i[1]),
                    recipe=recipe,
                    amount=i[0]
                )
            except Ingridient.DoesNotExist:
                if delete_recipe is True:
                    recipe.delete()


    def delete_tags(self, old_tags, old_recipe):
        for delete_tag in old_tags:
            old_recipe.tags.remove(delete_tag)

    def add_tags(self, tags, recipe):
        for add_item in tags:
            tag = get_object_or_404(Tag, slug=add_item)
            recipe.tags.add(tag)
        recipe.save()

    class Meta:
        model = Recipe
        fields = ('title', 'time', 'description', 'image',)
