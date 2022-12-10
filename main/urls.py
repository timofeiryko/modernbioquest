from django.urls import path, include
from . import views

app_name = 'main'   


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('personal/', views.personal, name='personal'),
    path('problems/', views.problems, name='problems'),
    path('problems/<str:slug>', views.question_page, name='question_page'),
    path('sections/<str:slug>', views.problems_by_section, name='section_url'),
    path('update_server/', views.update, name='update'),
    # auth
    path('accounts/', include('django.contrib.auth.urls'))
]