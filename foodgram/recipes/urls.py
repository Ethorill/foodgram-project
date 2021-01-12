from django.urls import include, path

from .views import (recipes_all,
                    recipe_detail,
                    recipe_profile,
                    add_favorite,
                    favorite_detail,
                    get_all_favor)


#router = DefaultRouter()
#router.register(r'hello', RecipeDetails)

urlpatterns = [
    path('', recipes_all, name='index'),
    path('recipe/<int:id>/',recipe_detail,  name='recipe_detail'),
    path('favorites/', add_favorite, name='add_favorite'),
    path('favorites/<int:id>/', favorite_detail, name='favorite_detail'),
    path('my_favorites/', get_all_favor, name='get_all_favor'),
    path('profile/<int:prof_id>/', recipe_profile, name='recipe_profile')
]


#urlpatterns += router.urls