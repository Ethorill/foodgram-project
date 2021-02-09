from django.urls import path

from .pdf_render import render_pdf_view
from .views import (recipes_all,
                    recipe_detail,
                    recipe_profile,
                    add_favorite,
                    favorite_remove,
                    get_all_favor,
                    add_sub,
                    remove_sub,
                    get_all_sub,
                    new_recipe,
                    get_all_ingr,
                    edit_recipe,
                    shoplist,
                    recipe_delete,
                    add_purchases,
                    remove_purchases)

urlpatterns = [
    path('', recipes_all, name='index'),
    path('recipe/<int:id>/', recipe_detail, name='recipe_detail'),
    path('new_recipe/', new_recipe, name='new_recipe'),
    path('edit_recipe/<int:recipe_id>/', edit_recipe, name='edit_r'),
    path('delete_recipe/<int:recipe_id>/', recipe_delete,
         name='recipe_delete'),
    path('favorites/', add_favorite, name='add_favorite'),
    path('favorites/<int:id>/', favorite_remove, name='favorite_detail'),
    path('my_favorites/', get_all_favor, name='get_all_favor'),
    path('subscriptions/', add_sub, name='add_sub'),
    path('subscriptions/<int:id>/', remove_sub, name='remove_sub'),
    path('my_subscriptions/', get_all_sub, name='get_all_sub'),
    path('profile/<int:prof_id>/', recipe_profile, name='recipe_profile'),
    path('ingredients/', get_all_ingr, name='get_all_ingr'),
    path('my_shoplist/', shoplist, name='shoplist'),
    path('purchases_pdf/', render_pdf_view, name='purch_pdf'),
    path('purchases/', add_purchases, name='purch'),
    path('purchases/<int:id>/', remove_purchases, name='rem_purch')
]

handler404 = "recipes.views.page_not_found"  # noqa
handler500 = "recipes.views.server_error"  # noqa
