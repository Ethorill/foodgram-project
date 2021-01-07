from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from .models import Recipe, RecipeIngridient


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
    queryset = Recipe.objects.all()
    return Response({'recipes': queryset}, template_name='indexNotAuth.html')


@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def recipe_detail(request, id):
    queryset = get_object_or_404(Recipe, id=id)
    return Response({'recipe': queryset},
                    template_name='singlePageNotAuth.html')
