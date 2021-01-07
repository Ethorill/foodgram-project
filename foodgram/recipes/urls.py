from django.urls import include, path

from .views import recipes_all, recipe_detail


#router = DefaultRouter()
#router.register(r'hello', RecipeDetails)

urlpatterns = [
    path('', recipes_all, name='index'),
    path('recipe/<int:id>/',recipe_detail,  name='recipe_detail')
]


#urlpatterns += router.urls