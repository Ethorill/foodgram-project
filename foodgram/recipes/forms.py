from django import forms
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Recipe, Tag, RecipeIngridient, Ingridient


class RecipeForm(forms.ModelForm):
    def save(self, commit=True, tags=None, request_ingr=None, old_recipe=None,
             old_tags=None, request=None,
             edit=False):
        recipe = super(RecipeForm, self).save(commit=False)
        if not tags:
            return redirect(reverse('new_recipe'))
        if not request_ingr:
            return redirect(reverse('new_recipe'))

        recipe.author = request.user
        recipe.save()
        if edit:
            self.delete_tags(old_tags, old_recipe)
            self.delete_ingr(old_recipe)

        for add_item in tags:
            tag = get_object_or_404(Tag, slug=add_item)
            recipe.tags.add(tag)
        recipe.save()

        for i in request_ingr:
            _, created = RecipeIngridient.objects.get_or_create(
                ingridient=get_object_or_404(Ingridient, title=i[1]),
                recipe=recipe,
                amount=i[0]
            )
            if not created:
                recipe.delete()
                return redirect(reverse('new_recipe'))
        self.save_m2m()
        return redirect(reverse('recipe_detail', args=[recipe.id]))

    def delete_ingr(self, old_recipe):
        old_ingr = old_recipe.recipes_ingridients.all()
        old_ingr.delete()

    def delete_tags(self, old_tags, old_recipe):
        for delete_tag in old_tags:
            old_recipe.tags.remove(delete_tag)

    class Meta:
        model = Recipe
        fields = ('title', 'time', 'description', 'image',)
