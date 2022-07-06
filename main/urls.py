from django.urls import path
from . import views

app_name = 'main'   


urlpatterns = [
    path('', views.problems, name='index'),
    path('about/', views.problems, name='about'),
    path('problems/', views.problems, name='problems')
]