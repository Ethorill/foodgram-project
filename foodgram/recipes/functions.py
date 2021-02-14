from django.db.models import Exists, OuterRef
from django.http import QueryDict

from recipes.models import FavoriteRecipe, ShopingList

BREAKFAST = 'breakfast'
LUNCH = 'lunch'
DINNER = 'dinner'

tags = [BREAKFAST, LUNCH, DINNER]


def get_ingr(obj):
    """
    Берет параметры из пост запроса и достает ингредиенты.
    :param obj: request.POST
    :return: ingredients_list
    """
    ingr = {parameter: value for parameter, value in obj.items() if
            parameter.startswith('nameIngredient') or parameter.startswith(
                'valueIngredient')}
    ingredients = [i for i in ingr.values()]
    ingredients_list = []
    while 0 <= len(ingredients) - 1:
        el1 = ingredients.pop()
        el2 = ingredients.pop()
        ingredients_list.append([el1, el2])
    return ingredients_list


def get_tags_from_post(obj):
    """
    Берет из пост запрсоа тэги.
    :param obj: request.POST
    :return: tags_list
    """
    tags_list = [tag for tag in obj if
                 tag in tags]
    return tags_list


def get_tags_from_get(obj):
    """
    Берет из гет запроса тэги.
    :param obj: request.GET.urlencode()
    :return: tags_list
    """
    tags = QueryDict(obj)
    tags_list = [i for i in tags.values() if
                 i in ['breakfast', 'lunch', 'dinner']]
    return tags_list


def check_auth_visitors(obj):
    """
    Проверка для выборки, зарегестрирован ли пользователь.
    :param obj: request
    :return: auth user or None
    """
    if obj.user.is_authenticated:
        return obj.user
    else:
        return None


def custom_filter_for_recipes(obj, tags_list, visitor):
    """
    Фильтр, который используеться для предотвращения повторения в коде,
    он принимает выборку и от определенного случая меняет фильтр.
    :param obj: QuerySet
    :param tags_list: list
    :param visitor: request.user
    :return: filtered recipes
    """
    if tags_list:
        recipes = obj.filter(tags__slug__in=tags_list).annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id'))
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        ).distinct()
        return recipes
    if not tags_list:
        recipes = obj.annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id'))
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        ).distinct()
        return recipes
