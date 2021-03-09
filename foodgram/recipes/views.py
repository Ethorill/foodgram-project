from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import (api_view,
                                       renderer_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from foodgram.settings import PAGINATOR_SIZE
from .forms import RecipeForm
from .functions import (get_ingr,
                        get_tags_from_post,
                        get_tags_from_get,
                        check_auth_visitors,
                        custom_filter_for_recipes)
from .models import (Recipe,
                     User,
                     FavoriteRecipe,
                     FollowUser,
                     Ingridient,
                     Tag,
                     ShopingList, RecipeIngridient)

paginator_size = PAGINATOR_SIZE


@login_required()
@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def edit_recipe(request, recipe_id):
    old_recipe = get_object_or_404(Recipe, id=recipe_id)
    old_tags = Tag.objects.all()
    edit = True
    if request.user != old_recipe.author:
        return redirect(reverse('index'))
    request_ingr = get_ingr(request.POST.dict())

    form = RecipeForm(request.POST or None,
                      files=request.FILES or None,
                      instance=old_recipe)

    tags = get_tags_from_post(request.POST)

    if form.is_valid():
        if form.check_tags(tags):
            return render(request, 'formRecipe.html',
                          {'form': form, 'tag_error': 'Не указали тэги',
                           'tags': old_tags, 'edit': edit,
                           'old_recipe': old_recipe})

        if form.check_ing(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'ingr_error': 'Вы не добавили ингредиенты',
                                                       'edit': edit,
                                                       'old_recipe': old_recipe})

        if form.check_amount_ingr(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'amount_error': 'Вы ввели отрицательное значение',
                                                       'edit': edit,
                                                       'old_recipe': old_recipe})

        if form.check_ingr_exist(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'ingr_exist_error': 'Такого ингредиента у нас, пока, нету',
                                                       'edit': edit,
                                                       'old_recipe': old_recipe})
        recipe = form.save(commit=False, tags=tags, old_recipe=old_recipe,
                           old_tags=old_tags, request_ingr=request_ingr,
                           edit=True, request=request)

        return recipe
    return render(request, 'formRecipe.html',
                  {'form': form, 'old_recipe': old_recipe,
                   'tags': old_tags, 'edit': edit})


@login_required()
def new_recipe(request):
    request_ingr = get_ingr(request.POST.dict())
    form = RecipeForm(request.POST or None, files=request.FILES or None)

    tags = get_tags_from_post(request.POST)

    if form.is_valid():
        if form.check_tags(tags):
            return render(request, 'formRecipe.html',
                          {'form': form, 'tag_error': 'Неуказали тэги'})

        if form.check_ing(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'ingr_error': 'Вы не добавили ингредиенты'})

        if form.check_amount_ingr(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'amount_error': 'Вы ввели отрицательное значение'})

        if form.check_ingr_exist(request_ingr):
            return render(request, 'formRecipe.html', {'form': form,
                                                       'ingr_exist_error': 'Такого ингредиента у нас, пока, нету'})
        recipe = form.save(commit=False, tags=tags, request_ingr=request_ingr,
                           request=request)

        return recipe
    return render(request, 'formRecipe.html', {'form': form, })


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user == recipe.author:
        recipe.delete()
    return redirect(reverse('index'))


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_all_ingr(request):
    search_ingr = request.GET['query']
    if search_ingr:
        filtered_ingr = Ingridient.objects.filter(
            title__icontains=search_ingr)[:5]
        result = []
        for i in filtered_ingr:
            unit = {
                'title': i.title,
                'dimension': i.measurement_unit
            }
            result.append(unit)
        return Response(data=result, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def recipes_all(request):
    tags_list = get_tags_from_get(request.GET.urlencode())
    visitor = check_auth_visitors(request)
    recipes = custom_filter_for_recipes(
        Recipe.objects.select_related('author'), tags_list, visitor)
    paginator = Paginator(recipes, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html',
                  {'page': page,
                   'paginator': paginator,
                   'tags_list': tags_list
                   },
                  )


@api_view(['GET'])
def recipe_detail(request, id):
    visitor = check_auth_visitors(request)

    recipe = Recipe.objects.select_related('author').filter(
        id=id
    ).annotate(
        fav=Exists(
            FavoriteRecipe.objects.filter(user=visitor,
                                          recipe_id=OuterRef('id'))
        ),
        shop=Exists(
            ShopingList.objects.filter(user=visitor,
                                       recipe_id=OuterRef('id'))
        ),
        follow=Exists(
            FollowUser.objects.filter(author=OuterRef('author'),
                                      user=visitor)
        ),

    ).distinct()

    ingredients = RecipeIngridient.objects.filter(recipe_id=id).values(
        'ingridient__title', 'ingridient__measurement_unit').annotate(
        sum=Sum('amount'))

    return render(request, 'singlePage.html',
                  {'recipe': recipe, 'ingredients': ingredients},
                  )


def recipe_profile(request, prof_id):
    visitor = check_auth_visitors(request)
    tags_list = get_tags_from_get(request.GET.urlencode())
    user = get_object_or_404(User, id=prof_id)
    recipes = custom_filter_for_recipes(user.recipes.all(), tags_list,
                                        visitor)
    paginator = Paginator(recipes, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'authorRecipe.html',
                  {"user": user,
                   'paginator': paginator,
                   'page': page,
                   'tags_list': tags_list},
                  )


@login_required()
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def add_favorite(request):
    recipe_id = request.data.get('id')

    if recipe_id is None:
        return Response({'success': False},
                        status=status.HTTP_400_BAD_REQUEST)

    _, created = FavoriteRecipe.objects.get_or_create(
        recipe_id=recipe_id,
        user=request.user)

    if created:
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response({'success': False})


@login_required()
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def favorite_remove(request, id):
    fav = get_object_or_404(FavoriteRecipe, recipe_id=id, user=request.user
                            )
    if request.user != fav.user:
        return Response({'success': False},
                        status=status.HTTP_400_BAD_REQUEST)
    fav.delete()
    return Response({'success': True}, status=status.HTTP_200_OK)


@login_required()
def get_all_favor(request):
    tags_list = get_tags_from_get(request.GET.urlencode())
    if tags_list:
        favorites = FavoriteRecipe.objects.select_related('user').filter(
            user=request.user, recipe__tags__slug__in=tags_list
        ).distinct()
    if not tags_list:
        favorites = FavoriteRecipe.objects.select_related('user').filter(
            user=request.user
        ).distinct()
    paginator = Paginator(favorites, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'favorite.html',
                  {'paginator': paginator, 'page': page,
                   'tags_list': tags_list},
                  )


@login_required()
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def add_sub(request):
    author_id = request.data.get('id')
    author = get_object_or_404(User, id=author_id)
    if request.user == author:
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    if FollowUser.objects.filter(user=request.user,
                                 author=author).exists():
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    _, created = FollowUser.objects.get_or_create(user=request.user,
                                                  author=author
                                                  )
    if created:
        return Response({'success': True}, status.HTTP_201_CREATED)
    return Response({'success': False}, status.HTTP_400_BAD_REQUEST)


@login_required()
@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def remove_sub(request, id):
    author = get_object_or_404(User, id=id)
    follow = FollowUser.objects.filter(user=request.user, author=author)

    if not follow.exists():
        return Response({'success': False}, status.HTTP_404_NOT_FOUND)

    follow.delete()
    return Response({'success': True}, status.HTTP_200_OK)


@login_required()
def get_all_sub(request):
    user = FollowUser.objects.select_related('user').filter(
        user_id=request.user)
    paginator = Paginator(user, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'myFollow.html',
                  {'paginator': paginator, 'page': page},
                  )


@login_required()
def shoplist(request):
    shop_list = ShopingList.objects.filter(user=request.user)
    return render(request, 'shopList.html', {'shop_list': shop_list},
                  )


@login_required()
@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def add_purchases(request):
    recipe_id = request.data.get('id')

    if recipe_id is None:
        return Response({'success': False},
                        status=status.HTTP_400_BAD_REQUEST)

    _, created = ShopingList.objects.get_or_create(
        recipe_id=recipe_id,
        user=request.user)

    if created:
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response({'success': False})


@login_required()
@api_view(['DELETE', 'GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def remove_purchases(request, id):
    purch = get_object_or_404(ShopingList, recipe_id=id, user=request.user)
    purch.delete()
    if request.method == 'DELETE':
        return Response({'success': True}, status=status.HTTP_200_OK)
    return redirect(reverse('shoplist'))
