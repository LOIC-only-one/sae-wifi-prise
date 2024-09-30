from django.urls import path
from .views import home, user_login, user_logout, plage_horaire

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),  
    path('logout/', user_logout, name='logout'),
    path('plage_horaires/', plage_horaire, name='plage_horaire'), 
]
