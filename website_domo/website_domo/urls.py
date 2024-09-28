from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website_app.urls')),  # Ajoutez cette ligne pour inclure les URLs de votre application
]
