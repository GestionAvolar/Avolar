from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLS pour la gestion de connexion (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Vos routes de projet
    path('', include('dashboard.urls')), 
]

# Ajout de cette section pour permettre l'accès aux fichiers importés
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)