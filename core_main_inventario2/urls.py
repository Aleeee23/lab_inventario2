from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views  #  IMPORTANTE

urlpatterns = [
    path('admin/', admin.site.urls),

    #  LOGOUT FUNCIONAL
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('', include('empleados_Alex.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)