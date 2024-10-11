from django.urls import path
from .views import home, user_login, user_logout, plage_horaire, plage_modifier, plage_delete, settings

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('plage_horaires/', plage_horaire, name='plage_horaire'),
    path('plage_modifier/<int:id>/', plage_modifier, name='plage_modifier'),
    path('plage_delete/<int:id>/', plage_delete, name='plage_delete'),
    path('settings/', settings, name='settings'),
]
