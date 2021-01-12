from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, renderer_classes, \
    authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe, RecipeIngridient, User, FavoriteRecipe
from .serializers import FavoriteRecipeSerializer


# class RecipeDetails(generics.RetrieveAPIView):
#     queryset = Recipe.objects.all()
#     renderer_classes = [TemplateHTMLRenderer]
#     lookup_field = 'pk'
#     def get(self, *args, **kwargs):
#         self.object = self.get_object()
#         return Response({'recipe': self.object}, template_name='lalal.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipes_all(request):
    recipes = Recipe.objects.all()
    return Response({'recipes': recipes}, template_name='indexNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return Response({'recipe': recipe},
                    template_name='singlePageNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def recipe_profile(request, prof_id):
    user = get_object_or_404(User, id=prof_id)
    recipes = user.recipes.all()
    return Response({"user": user, 'recipes': recipes},
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
def favorite_detail(request, id):
    fav = get_object_or_404(FavoriteRecipe, recipe_id=id
    )
    if request.user != fav.user:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
    fav.delete()
    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
@permission_classes([IsAuthenticated])
def get_all_favor(request):
    favorites = FavoriteRecipe.objects.select_related('user').filter(user=request.user)
    return Response({'recipes': favorites},
                    template_name='favorite.html')