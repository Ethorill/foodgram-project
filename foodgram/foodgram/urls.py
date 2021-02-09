from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.flatpages import views

urlpatterns = [
    path('', include('recipes.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('about/', views.flatpage, {'url': '/about/'}, name='about'),
    path('author/', views.flatpage, {'url': '/author/'}, name='author'),
    path('technologies/', views.flatpage, {'url': '/technologies/'},
         name='technologies'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT
                          )
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT
                          )
