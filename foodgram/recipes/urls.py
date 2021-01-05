from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

from .views import recipes_all


#router = DefaultRouter()
#router.register(r'hello', RecipeDetails)

urlpatterns = [
    path("hello/", recipes_all)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT
                          )
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT
                          )

#urlpatterns += router.urls