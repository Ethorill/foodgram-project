from django.http import QueryDict


def get_ingr(obj):
    """
    Берет параметры из пост запроса и достает ингредиенты.
    :param obj: request.POST
    :return: ingredients_list
    """
    ingr = {k: l for k, l in obj.items() if
            k.startswith('nameIngredient') or k.startswith('valueIngredient')}
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
                 tag in ['breakfast', 'lunch', 'dinner']]
    return tags_list


def get_tags_from_get(obj):
    """
    Берет из гет запроса тэги.
    :param obj: request.GET.urlencode()
    :return: tags_list
    """
    tags = QueryDict(obj)
    tags_list = [i for i in tags.values() if
                 i in ['dinner', 'lunch', 'breakfast']]
    return tags_list


def check_auth_visitors(obj):
    """
    Проверка для выборки, зарегестрирован ли пользователь.
    :param obj: request
    :return: auth user or None
    """
    if obj.user.is_authenticated:
        return obj.user
    if not obj.user.is_authenticated:
        return None
