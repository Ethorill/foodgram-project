def get_ingr(obj):
    """
    Функция для получения ингридиентов из POST запроса
    :param obj: Словарь
    :return: Список
    """
    ingr = {k: l for k, l in obj.items() if
            k.startswith('nameIngredient') or k.startswith('valueIngredient')}
    lil = [i for i in ingr.values()]
    res = []
    while 0 <= len(lil) - 1:
        el1 = lil.pop()
        el2 = lil.pop()
        res.append([el1, el2])
    return res
