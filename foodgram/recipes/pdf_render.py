import os

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse
from xhtml2pdf import pisa

from foodgram import settings
from recipes.models import ShopingList, RecipeIngridient, Recipe


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path


def render_pdf_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    shop_list = ShopingList.objects.filter(user=request.user)
    recipe_id = []
    for i in shop_list:
        recipe_id.append(i.recipe.id)
    recipe_list = Recipe.objects.filter(id__in=recipe_id)
    ingredients_list = (
        RecipeIngridient.objects.filter(
            recipe_id__in=recipe_id
        ).values(
            'ingridient__title', 'ingridient__measurement_unit'
        ).annotate(sum=Sum('amount'))
    )

    template_path = 'shop_list_pdf.html'
    context = {'recipes_list': recipe_list, 'ingredients_list': ingredients_list}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ingr_for_{request.user}.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=fetch_pdf_resources)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
