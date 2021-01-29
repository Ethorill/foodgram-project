from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, \
    permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from .models import Recipe, User, FavoriteRecipe, FollowUser, RecipeIngridient, \
    Ingridient, Tag
from .forms import RecipeForm
from .functions import get_ingr


@api_view(['GET', 'POST'])
@renderer_classes([TemplateHTMLRenderer])
def new_recipe(request):
    if request.method == 'POST':
        req = get_ingr(request.POST.dict())
        form = RecipeForm(request.POST or None, files=request.FILES or None)

        tags = [i for i in request.POST if
                i in ['breakfast', 'lunch', 'dinner']]

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            for item in tags:
                tag = Tag.objects.get(slug=item)
                recipe.tag.add(tag)
            recipe.save()

            for i in req:
                RecipeIngridient.objects.create(
                    ingridient=Ingridient.objects.get(title=i[1]),
                    recipe=recipe,
                    amount=i[0]
                )
            form.save_m2m()
            return redirect('index')
        return Response(template_name='formRecipe.html',
                        data={'form': form, 'tags': tags})

    form = RecipeForm
    return Response(template_name='formRecipe.html', data={'form': form})


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipes_all(request):
    tags = QueryDict(request.GET.urlencode())
    tags_list = [i for i in tags.values() if
                 i in ['dinner', 'lunch', 'breakfast']]

    if request.user.is_authenticated:
        if tags_list:
            recipes = Recipe.objects.select_related('author').filter(
                tag__slug__in=tags_list
            ).annotate(
                fav=Exists(
                    FavoriteRecipe.objects.filter(user=request.user,
                                                  recipe_id=OuterRef('id'))
                )
            ).distinct()

        if not tags_list:
            recipes = Recipe.objects.select_related('author').annotate(
                fav=Exists(
                    FavoriteRecipe.objects.filter(user=request.user)
                )
            )

    if not request.user.is_authenticated:
        if tags_list:
            recipes = Recipe.objects.select_related('author').filter(
                tag__slug__in=tags_list
            ).distinct()

        if not tags_list:
            recipes = Recipe.objects.select_related('author')

    paginator = Paginator(recipes, 6)
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
    recipe = get_object_or_404(Recipe, id=id)
    check_follow = recipe.following_recipe.exists()
    return Response({'recipe': recipe,
                     'check_follow': check_follow},
                    template_name='singlePageNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipe_profile(request, prof_id):
    tags = QueryDict(request.GET.urlencode())
    tags_list = [i for i in tags.values() if
                 i in ['dinner', 'lunch', 'breakfast']]

    user = get_object_or_404(User, id=prof_id)

    if request.user.is_authenticated:
        if tags_list:
            recipes = user.recipes.filter(tag__slug__in=tags_list).annotate(
                fav=Exists(
                    FavoriteRecipe.objects.filter(user=request.user)
                )
            ).distinct()

        if not tags_list:
            recipes = user.recipes.all().annotate(
                fav=Exists(
                    FavoriteRecipe.objects.filter(user=request.user)
                )
            ).distinct()

    if not request.user.is_authenticated:
        if tags_list:
            recipes = user.recipes.filter(tag__slug__in=tags_list).distinct()

        if not tags_list:
            recipes = user.recipes.all()

    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return Response({"user": user,
                     'paginator': paginator,
                     'page': page,
                     'tags_list': tags_list
                     },
                    template_name='authorRecipe.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def add_favorite(request):
    recipe_id = request.data['id']

    if recipe_id is None:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    obj, created = FavoriteRecipe.objects.get_or_create(
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
    favorites = FavoriteRecipe.objects.select_related('user').filter(
        user=request.user
    )
    paginator = Paginator(favorites, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return Response({'paginator': paginator, 'page': page},
                    template_name='favorite.html')


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def add_sub(request):
    author_id = request.data['id']
    author = get_object_or_404(User, id=author_id)
    if request.user == author:
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    if FollowUser.objects.filter(user=request.user, author=author).exists():
        return Response({'success': False}, status.HTTP_403_FORBIDDEN)

    obj, created = FollowUser.objects.get_or_create(user=request.user,
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
    paginator = Paginator(user, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return Response({'paginator': paginator, 'page': page},
                    template_name='myFollow.html')
