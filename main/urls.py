from django.urls import path
from . import views

app_name = 'main'   


urlpatterns = [
    path('', views.problems, name='index'),
    path('about/', views.problems, name='about'),
    path('problems/', views.problems, name='problems'),
    path('update_server/', views.update, name='update'),
    path('problems/<str:slug>', views.question_page, name='question_page'),
    path('sections/<str:slug>', views.problems_by_section, name='section_url')
]