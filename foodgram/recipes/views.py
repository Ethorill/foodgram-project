from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import QueryDict
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
                        check_auth_visitors)
from .models import (Recipe,
                     User,
                     FavoriteRecipe,
                     FollowUser,
                     RecipeIngridient,
                     Ingridient,
                     Tag,
                     ShopingList)

paginator_size = PAGINATOR_SIZE


class RecipeActionCreate:
    def check_error_tag(self, tags, form, template_name, tag_msg):
        if not tags:
            tag_error = tag_msg
            return Response({'form': form, 'tag_error': tag_error},
                            template_name=template_name)

    def check_error_ingr(self, request_ingr, form, template_name):
        if not request_ingr:
            recipe_error = 'Обязательное поле'
            return Response(
                {'form': form, 'recipe_error': recipe_error},
                template_name=template_name)

    def add_ingr(self, request_ingr, recipe, form, delete_recipe: bool,
                 template_name):

        for i in request_ingr:
            try:
                RecipeIngridient.objects.create(
                    ingridient=get_object_or_404(Ingridient, title=i[1]),
                    recipe=recipe,
                    amount=i[0]
                )
            except Ingridient.DoesNotExist:
                recipe_error = 'Произошла ошибка при добавлении ингридиента,' \
                               ' возмможно вы ввели не существующий'

                if delete_recipe is True:
                    recipe.delete()

                return Response(
                    {'form': form, 'recipe_error': recipe_error},
                    template_name=template_name)

    def delete_tags(self, old_tags, old_recipe):
        for delete_tag in old_tags:
            old_recipe.tag.remove(delete_tag)

    def add_tags(self, tags, recipe):
        for add_item in tags:
            tag = Tag.objects.get(slug=add_item)
            recipe.tag.add(tag)
        recipe.save()


action_recipe = RecipeActionCreate()


@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def edit_recipe(request, recipe_id):
    old_recipe = get_object_or_404(Recipe, id=recipe_id)
    old_tags = Tag.objects.all()
    old_ingr = old_recipe.recipes_ingridients.all()
    if request.user != old_recipe.author:
        return redirect(reverse('index'))
    request_ingr = get_ingr(request.POST.dict())

    form = RecipeForm(request.POST or None,
                      files=request.FILES or None,
                      instance=old_recipe)

    tags = get_tags_from_post(request.POST)

    if form.is_valid():
        action_recipe.check_error_tag(tags=tags, form=form,
                                      template_name='formChangeRecipe.htm',
                                      tag_msg='Вы убрали тэги полностью')
        action_recipe.check_error_ingr(request_ingr, form,
                                       template_name='formChangeRecipe.htm')
        recipe = form.save(commit=False)
        recipe.save()
        action_recipe.delete_tags(old_tags, old_recipe)
        action_recipe.add_tags(tags=tags, recipe=recipe)
        old_ingr.delete()
        action_recipe.add_ingr(request_ingr, recipe, form, delete_recipe=False,
                               template_name='formChangeRecipe.htm')
        form.save_m2m()
        return redirect(reverse('recipe_detail', args=[recipe.id]))
    return Response(template_name='formChangeRecipe.html',
                    data={'form': form, 'old_recipe': old_recipe,
                          'tags': old_tags})


@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
def new_recipe(request):
    request_ingr = get_ingr(request.POST.dict())
    form = RecipeForm(request.POST or None, files=request.FILES or None)

    tags = get_tags_from_post(request.POST)

    if form.is_valid():
        action_recipe.check_error_tag(tags=tags, form=form,
                                      template_name='formRecipe.htm',
                                      tag_msg='Вы не указали тэги')
        action_recipe.check_error_ingr(request_ingr, form,
                                       template_name='formRecipe.htm')
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        action_recipe.add_tags(tags, recipe)
        action_recipe.add_ingr(request_ingr, recipe, form, delete_recipe=True,
                               template_name='formRecipe.htm')

        form.save_m2m()
        return redirect(reverse('recipe_detail', args=[recipe.id]))
    return Response(template_name='formRecipe.html', data={'form': form, })


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect(reverse('index'))
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


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipes_all(request):
    tags_list = get_tags_from_get(request.GET.urlencode())
    visitor = check_auth_visitors(request)

    # Я пытался сократить этот момент, но без поломок я не смог
    if tags_list:
        recipes = Recipe.objects.select_related('author').filter(
            tag__slug__in=tags_list
        ).annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id'))
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        ).distinct()

    if not tags_list:
        recipes = Recipe.objects.select_related('author').annotate(
        ).annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id'))
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        )

    paginator = Paginator(recipes, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return Response({'page': page,
                     'paginator': paginator,
                     'tags_list': tags_list
                     },
                    template_name='indexNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
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
        )
    ).distinct()

    return Response({'recipe': recipe},
                    template_name='singlePageNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipe_profile(request, prof_id):
    visitor = check_auth_visitors(request)
    tags_list = get_tags_from_get(request.GET.urlencode())
    user = get_object_or_404(User, id=prof_id)

    if tags_list:
        recipes = user.recipes.filter(tag__slug__in=tags_list).annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id'))
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        ).distinct()

    if not tags_list:
        recipes = user.recipes.all().annotate(
            fav=Exists(
                FavoriteRecipe.objects.filter(user=visitor,
                                              recipe_id=OuterRef('id')),
            ),
            shop=Exists(
                ShopingList.objects.filter(user=visitor,
                                           recipe_id=OuterRef('id'))
            )
        ).distinct()

    paginator = Paginator(recipes, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return Response({"user": user,
                     'paginator': paginator,
                     'page': page,
                     'tags_list': tags_list},
                    template_name='authorRecipe.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def add_favorite(request):
    recipe_id = request.data.get('id', None)

    if recipe_id is None:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    _, created = FavoriteRecipe.objects.get_or_create(
        recipe_id=recipe_id,
        user=request.user)

    if created:
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response({'success': False})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def favorite_remove(request, id):
    fav = get_object_or_404(FavoriteRecipe, recipe_id=id, user=request.user
                            )
    if request.user != fav.user:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
    fav.delete()
    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def get_all_favor(request):
    tags_list = get_tags_from_get(request.GET.urlencode())
    if tags_list:
        favorites = FavoriteRecipe.objects.select_related('user').filter(
            user=request.user, recipe__tag__slug__in=tags_list
        )
    if not tags_list:
        favorites = FavoriteRecipe.objects.select_related('user').filter(
            user=request.user
        )
    paginator = Paginator(favorites, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return Response(
        {'paginator': paginator, 'page': page, 'tags_list': tags_list},
        template_name='favorite.html')


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def add_sub(request):
    author_id = request.data.get('id', None)
    author = get_object_or_404(User, id=author_id)
    if request.user == author:
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    if FollowUser.objects.filter(user=request.user, author=author).exists():
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    _, created = FollowUser.objects.get_or_create(user=request.user,
                                                  author=author
                                                  )
    if created:
        return Response({'success': True}, status.HTTP_201_CREATED)
    return Response({'success': False}, status.HTTP_400_BAD_REQUEST)


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


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def get_all_sub(request):
    user = FollowUser.objects.select_related('user').filter(
        user_id=request.user)
    paginator = Paginator(user, paginator_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return Response({'paginator': paginator, 'page': page},
                    template_name='myFollow.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def shoplist(request):
    shop_list = ShopingList.objects.filter(user=request.user)
    return Response({'shop_list': shop_list}, template_name='shopList.html')


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def add_purchases(request):
    recipe_id = request.data.get('id', None)

    if recipe_id is None:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    obj, created = ShopingList.objects.get_or_create(
        recipe_id=recipe_id,
        user=request.user)

    if created:
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response({'success': False})


@api_view(['DELETE', 'GET'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def remove_purchases(request, id):
    purch = get_object_or_404(ShopingList, recipe_id=id, user=request.user)
    purch.delete()
    if request.method == 'DELETE':
        return Response({'success': True}, status=status.HTTP_200_OK)
    return redirect(reverse('shoplist'))


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
