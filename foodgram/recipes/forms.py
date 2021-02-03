from django import forms

from .models import Recipe, Tag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'time', 'description', 'image')
