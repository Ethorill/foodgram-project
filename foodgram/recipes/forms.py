from django import forms
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Recipe, Tag, RecipeIngridient, Ingridient


class RecipeForm(forms.ModelForm):
    def save(self, commit=True, tags=None, request_ingr=None, old_recipe=None,
             old_tags=None, request=None,
             edit=False):

        recipe = super(RecipeForm, self).save(commit=False)

        recipe.author = request.user
        recipe.save()

        if edit:
            self.delete_tags(old_tags, old_recipe)
            self.delete_ingr(old_recipe)

        for add_item in tags:
            tag = get_object_or_404(Tag, slug=add_item)
            recipe.tags.add(tag)
        recipe.save()

        for ingredient_values in request_ingr:
            RecipeIngridient.objects.create(
                ingridient=Ingridient.objects.get(
                    title=ingredient_values[1]),
                recipe=recipe,
                amount=ingredient_values[0]
            )

        self.save_m2m()
        return redirect(reverse('recipe_detail', args=[recipe.id]))

    def check_ingr_exist(self, request_ingr):
        for ingredient in request_ingr:
            try:
                Ingridient.objects.get(title=ingredient[1])
            except Ingridient.DoesNotExist:
                return True
            return False

    def check_amount_ingr(self, request_ingr):
        for ingredients_param in request_ingr:
            # Проверка, ввел ли пользователь отрицательное
            # число в количество ингредиентов
            if int(ingredients_param[0]) <= 0:
                return True
            return False

    def check_ing(self, request_ingr):
        if not request_ingr:
            return True
        return False

    def check_tags(self, tags):
        if not tags:
            # Проверка, получены ли тэги
            return True
        return False

    def delete_ingr(self, old_recipe):
        old_ingr = old_recipe.recipes_ingridients.all()
        old_ingr.delete()

    def delete_tags(self, old_tags, old_recipe):
        for delete_tag in old_tags:
            old_recipe.tags.remove(delete_tag)

    class Meta:
        model = Recipe
        fields = ('title', 'time', 'description', 'image',)
