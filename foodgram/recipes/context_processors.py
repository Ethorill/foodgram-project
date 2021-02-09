from .models import ShopingList


def shop_count(request):
    if request.user.is_authenticated:
        count = ShopingList.objects.filter(user=request.user).count()
        return {"shop_count": count}
    return {"shop_count": 0}
