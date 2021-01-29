from django.urls import include, path

from .views import (recipes_all,
                    recipe_detail,
                    recipe_profile,
                    add_favorite,
                    favorite_remove,
                    get_all_favor,
                    add_sub,
                    remove_sub,
                    get_all_sub,
                    new_recipe)


#router = DefaultRouter()
#router.register(r'hello', RecipeDetails)

urlpatterns = [
    path('', recipes_all, name='index'),
    path('recipe/<int:id>/',recipe_detail,  name='recipe_detail'),
    path('new_recipe/', new_recipe, name='new_recipe'),
    path('favorites/', add_favorite, name='add_favorite'),
    path('favorites/<int:id>/', favorite_remove, name='favorite_detail'),
    path('my_favorites/', get_all_favor, name='get_all_favor'),
    path('subscriptions/', add_sub, name='add_sub'),
    path('subscriptions/<int:id>/', remove_sub, name='remove_sub'),
    path('my_subscriptions/', get_all_sub, name='get_all_sub'),
    path('profile/<int:prof_id>/', recipe_profile, name='recipe_profile')
]


